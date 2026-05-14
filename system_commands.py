#!/usr/bin/env python3
"""
System Helper Commands for Dual-Mode Bot
Extends VRChat bot with system management commands.
"""

import os
import sys
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from system_helper import SystemHelper, ScheduledTasks

class SystemCommands:
    """System helper commands for VRChat bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.system_helper = SystemHelper()
        self.scheduled_tasks = ScheduledTasks(self.system_helper)
        
    async def handle_system_command(self, command: str, args: List[str], sender: str) -> str:
        """Handle system-related commands."""
        cmd = command.lower().strip()
        
        if cmd == 'status':
            return await self.cmd_status(args, sender)
        elif cmd == 'cleanup':
            return await self.cmd_cleanup(args, sender)
        elif cmd == 'scan':
            return await self.cmd_scan(args, sender)
        elif cmd == 'duplicates':
            return await self.cmd_duplicates(args, sender)
        elif cmd == 'disk':
            return await self.cmd_disk(args, sender)
        elif cmd == 'health':
            return await self.cmd_health(args, sender)
        elif cmd == 'mode':
            return await self.cmd_mode(args, sender)
        elif cmd == 'optimize':
            return await self.cmd_optimize(args, sender)
        elif cmd == 'temp':
            return await self.cmd_temp(args, sender)
        else:
            return f"Unknown system command: {cmd}. Available: status, cleanup, scan, duplicates, disk, health, mode, optimize, temp"
    
    async def cmd_status(self, args: List[str], sender: str) -> str:
        """Show system status."""
        try:
            info = self.system_helper.get_system_info()
            
            return f"""🖥️ **System Status**
💻 **Platform**: {info.platform}
🧠 **CPU Cores**: {info.cpu_count}
💾 **Memory**: {info.memory_available / (1024**3):.1f} GB available
💿 **Storage**: {info.disk_free / (1024**3):.1f} GB free ({(info.disk_used / info.disk_total * 100):.1f}% used)
🐍 **Python**: {info.python_version}
⏰ **Check Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
        except Exception as e:
            return f"❌ Error getting system status: {e}"
    
    async def cmd_cleanup(self, args: List[str], sender: str) -> str:
        """Perform system cleanup."""
        try:
            self.bot.logger.info(f"User {sender} requested system cleanup")
            
            # Perform cleanup
            results = self.system_helper.optimize_disk_space()
            
            space_freed_mb = results['space_freed'] / (1024 * 1024)
            operations_count = len(results['operations'])
            
            return f"""🧹 **System Cleanup Complete**
💾 **Space Freed**: {space_freed_mb:.1f} MB
🔧 **Operations**: {operations_count}
📋 **Actions Taken**: {', '.join(results['operations'][:3])}{'...' if len(results['operations']) > 3 else ''}

✅ System optimized successfully!"""
            
        except Exception as e:
            return f"❌ Cleanup failed: {e}"
    
    async def cmd_scan(self, args: List[str], sender: str) -> str:
        """Scan for system issues."""
        try:
            self.bot.logger.info(f"User {sender} requested system scan")
            
            report = self.system_helper.get_disk_usage_report()
            
            # Format recommendations
            recommendations = report.get('recommendations', [])
            if not recommendations:
                recommendations = ["✅ No issues found"]
            
            # Find large directories
            large_dirs = report.get('large_directories', {})
            top_dirs = list(large_dirs.items())[:3]
            
            return f"""🔍 **System Scan Results**
📊 **Disk Usage**: 
{self._format_disk_usage(report.get('disk_usage', {}))}

📁 **Large Directories**:
{self._format_large_dirs(top_dirs)}

⚠️ **Recommendations**:
{chr(10).join(f'• {rec}' for rec in recommendations[:5])}

🔍 **Scan completed at**: {datetime.now().strftime('%H:%M:%S')}"""
            
        except Exception as e:
            return f"❌ Scan failed: {e}"
    
    async def cmd_duplicates(self, args: List[str], sender: str) -> str:
        """Find and remove duplicate files."""
        try:
            directory = args[0] if args else os.path.expanduser('~/Downloads')
            
            self.bot.logger.info(f"User {sender} requested duplicate scan in {directory}")
            
            duplicates = self.system_helper.find_duplicate_files(directory)
            
            if not duplicates:
                return f"🔍 **No duplicates found** in {directory}"
            
            total_duplicates = sum(len(paths) - 1 for _, paths in duplicates)
            total_space = 0
            
            # Calculate space that could be freed
            for file_hash, paths in duplicates:
                if len(paths) > 1:
                    file_size = os.path.getsize(paths[0]) if os.path.exists(paths[0]) else 0
                    total_space += file_size * (len(paths) - 1)
            
            # Auto-remove if requested
            if len(args) > 1 and args[1].lower() == 'remove':
                removed = self.system_helper.remove_duplicates(duplicates)
                space_freed_mb = total_space / (1024 * 1024)
                
                return f"""🗑️ **Duplicate Cleanup Complete**
📁 **Directory**: {directory}
🔍 **Duplicates Found**: {total_duplicates}
🗑️ **Duplicates Removed**: {removed}
💾 **Space Freed**: {space_freed_mb:.1f} MB"""
            else:
                space_savable_mb = total_space / (1024 * 1024)
                
                return f"""🔍 **Duplicate Files Found**
📁 **Directory**: {directory}
🔍 **Duplicate Groups**: {len(duplicates)}
📊 **Total Duplicates**: {total_duplicates}
💾 **Space that could be freed**: {space_savable_mb:.1f} MB

💡 **To remove duplicates**: !duplicates {directory} remove"""
            
        except Exception as e:
            return f"❌ Duplicate scan failed: {e}"
    
    async def cmd_disk(self, args: List[str], sender: str) -> str:
        """Show detailed disk usage."""
        try:
            report = self.system_helper.get_disk_usage_report()
            
            return f"""💿 **Disk Usage Report**
{self._format_disk_usage(report.get('disk_usage', {}))}

📊 **File Type Distribution**:
{self._format_file_types(report.get('file_type_distribution', {}))}

📈 **Storage Recommendations**:
{chr(10).join(f'• {rec}' for rec in report.get('recommendations', [])[:3])}"""
            
        except Exception as e:
            return f"❌ Disk analysis failed: {e}"
    
    async def cmd_health(self, args: List[str], sender: str) -> str:
        """Show system health status."""
        try:
            info = self.system_helper.get_system_info()
            
            # Calculate health metrics
            memory_percent = (1 - info.memory_available / info.memory_total) * 100 if info.memory_total > 0 else 0
            disk_percent = (info.disk_used / info.disk_total) * 100 if info.disk_total > 0 else 0
            
            # Health status
            health_status = "🟢 Good"
            if memory_percent > 80 or disk_percent > 90:
                health_status = "🔴 Critical"
            elif memory_percent > 60 or disk_percent > 80:
                health_status = "🟡 Warning"
            
            return f"""🏥 **System Health**
{health_status} **Overall Status**

💾 **Memory Usage**: {memory_percent:.1f}%
💿 **Disk Usage**: {disk_percent:.1f}%
🖥️ **Platform**: {info.platform}
⏰ **Uptime**: {self._get_uptime()}

📋 **Health Tips**:
{self._get_health_tips(memory_percent, disk_percent)}"""
            
        except Exception as e:
            return f"❌ Health check failed: {e}"
    
    async def cmd_mode(self, args: List[str], sender: str) -> str:
        """Switch bot modes."""
        try:
            if not args:
                current_mode = getattr(self.bot, 'current_mode', 'unknown')
                return f"🔄 **Current Mode**: {current_mode}\n\nAvailable modes: vrchat, standby, system_helper"
            
            new_mode = args[0].lower()
            
            if hasattr(self.bot, 'switch_mode'):
                from dual_mode_bot import BotMode
                
                mode_map = {
                    'vrchat': BotMode.VRCHAT,
                    'standby': BotMode.STANDBY,
                    'system_helper': BotMode.SYSTEM_HELPER,
                    'minimal': BotMode.MINIMAL_VRCHAT
                }
                
                if new_mode in mode_map:
                    success = await self.bot.switch_mode(mode_map[new_mode])
                    if success:
                        return f"✅ **Mode switched to**: {new_mode}"
                    else:
                        return f"❌ **Failed to switch mode**: {new_mode}"
                else:
                    return f"❌ **Unknown mode**: {new_mode}"
            else:
                return "❌ Mode switching not available in current bot version"
                
        except Exception as e:
            return f"❌ Mode switch failed: {e}"
    
    async def cmd_optimize(self, args: List[str], sender: str) -> str:
        """Perform system optimization."""
        try:
            self.bot.logger.info(f"User {sender} requested system optimization")
            
            # Comprehensive optimization
            results = self.system_helper.optimize_disk_space()
            
            # Additional optimizations
            temp_cleaned = self.system_helper.clean_temp_files()
            
            space_freed_mb = results['space_freed'] / (1024 * 1024)
            temp_files = temp_cleaned['temp_files']
            
            return f"""⚡ **System Optimization Complete**
💾 **Disk Space Freed**: {space_freed_mb:.1f} MB
🗑️ **Temp Files Removed**: {temp_files}
🔧 **Optimizations Applied**: {len(results['operations'])}

📋 **Summary**:
{chr(10).join(f'• {op}' for op in results['operations'][:3])}

✅ System is now optimized!"""
            
        except Exception as e:
            return f"❌ Optimization failed: {e}"
    
    async def cmd_temp(self, args: List[str], sender: str) -> str:
        """Clean temporary files."""
        try:
            self.bot.logger.info(f"User {sender} requested temp cleanup")
            
            cleaned = self.system_helper.clean_temp_files()
            
            return f"""🗑️ **Temporary Files Cleanup**
📁 **Temp Files Removed**: {cleaned['temp_files']}
🗂️ **Cache Dirs Cleaned**: {cleaned['cache_dirs']}
📝 **Log Files Cleaned**: {cleaned['log_files']}
💾 **Space Freed**: {cleaned['space_freed'] / (1024*1024):.1f} MB

✅ Temporary files cleaned successfully!"""
            
        except Exception as e:
            return f"❌ Temp cleanup failed: {e}"
    
    def _format_disk_usage(self, disk_usage: Dict) -> str:
        """Format disk usage information."""
        if not disk_usage:
            return "No disk usage data available"
        
        lines = []
        for mount, usage in disk_usage.items():
            lines.append(f"📁 {mount}: {usage['used'] / (1024**3):.1f} GB used / {usage['total'] / (1024**3):.1f} GB ({usage['percent']:.1f}%)")
        
        return '\n'.join(lines)
    
    def _format_large_dirs(self, large_dirs: List) -> str:
        """Format large directories information."""
        if not large_dirs:
            return "No large directories found"
        
        lines = []
        for dir_path, size in large_dirs:
            size_mb = size / (1024 * 1024)
            dir_name = os.path.basename(dir_path) or dir_path
            lines.append(f"📁 {dir_name}: {size_mb:.1f} MB")
        
        return '\n'.join(lines)
    
    def _format_file_types(self, file_types: Dict) -> str:
        """Format file type distribution."""
        if not file_types:
            return "No file type data available"
        
        lines = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"📄 {ext or 'no extension'}: {count} files")
        
        return '\n'.join(lines)
    
    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            import psutil
            uptime_seconds = psutil.boot_time()
            uptime = time.time() - uptime_seconds
            
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    def _get_health_tips(self, memory_percent: float, disk_percent: float) -> str:
        """Get health tips based on system metrics."""
        tips = []
        
        if memory_percent > 80:
            tips.append("💡 Consider closing unused applications")
        elif memory_percent > 60:
            tips.append("💡 Monitor memory usage")
        
        if disk_percent > 90:
            tips.append("💡 Urgent: Clean up disk space")
        elif disk_percent > 80:
            tips.append("💡 Consider disk cleanup")
        elif disk_percent > 70:
            tips.append("💡 Monitor disk usage")
        
        if not tips:
            tips.append("✅ System looks healthy!")
        
        return '\n'.join(tips)

# Integration with existing bot
def integrate_system_commands(bot):
    """Integrate system commands with VRChat bot."""
    system_commands = SystemCommands(bot)
    
    # Store reference for later use
    bot.system_commands = system_commands
    
    # Override handle_command to include system commands
    original_handle_command = bot.handle_command
    
    def enhanced_handle_command(command: str, sender: str) -> str:
        # Check if it's a system command
        if command.startswith('!'):
            cmd_without_prefix = command[1:]
            cmd_parts = cmd_without_prefix.split()
            
            if cmd_parts and cmd_parts[0] in ['status', 'cleanup', 'scan', 'duplicates', 'disk', 'health', 'mode', 'optimize', 'temp']:
                # Handle system command asynchronously
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, create a task
                        task = asyncio.create_task(
                            system_commands.handle_system_command(cmd_parts[0], cmd_parts[1:], sender)
                        )
                        return "System command processing..."
                    else:
                        # If loop is not running, run it
                        return loop.run_until_complete(
                            system_commands.handle_system_command(cmd_parts[0], cmd_parts[1:], sender)
                        )
                except Exception as e:
                    return f"❌ System command error: {e}"
        
        # Use original command handler for non-system commands
        return original_handle_command(command, sender)
    
    bot.handle_command = enhanced_handle_command
    
    return system_commands
