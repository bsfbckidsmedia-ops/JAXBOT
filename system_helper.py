#!/usr/bin/env python3
"""
System Helper Module for VRChat Bot
Provides disk cleanup, duplicate detection, and system optimization features.
"""

import os
import sys
import shutil
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import platform

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class SystemInfo:
    """System information data structure."""
    platform: str
    python_version: str
    cpu_count: int
    memory_total: int
    memory_available: int
    disk_total: int
    disk_free: int
    disk_used: int

class SystemHelper:
    """System helper for disk cleanup and optimization."""
    
    def __init__(self):
        self.logger = logging.getLogger('SystemHelper')
        self.platform = platform.system().lower()
        self.cleanup_stats = {
            'files_removed': 0,
            'space_freed': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0
        }
        
    def get_system_info(self) -> SystemInfo:
        """Get comprehensive system information."""
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SystemInfo(
                platform=platform.system(),
                python_version=sys.version.split()[0],
                cpu_count=psutil.cpu_count(),
                memory_total=memory.total,
                memory_available=memory.available,
                disk_total=disk.total,
                disk_free=disk.free,
                disk_used=disk.used
            )
        else:
            # Fallback without psutil
            statvfs = os.statvfs('/')
            total = statvfs.f_frsize * statvfs.f_blocks
            free = statvfs.f_frsize * statvfs.f_bavail
            
            return SystemInfo(
                platform=platform.system(),
                python_version=sys.version.split()[0],
                cpu_count=os.cpu_count(),
                memory_total=0,
                memory_available=0,
                disk_total=total,
                disk_free=free,
                disk_used=total - free
            )
    
    def scan_directory_size(self, directory: str, max_depth: int = 3) -> Dict[str, int]:
        """Scan directory and return size information."""
        sizes = {}
        
        try:
            for root, dirs, files in os.walk(directory):
                # Limit depth to prevent excessive scanning
                depth = root[len(directory):].count(os.sep)
                if depth > max_depth:
                    continue
                    
                total_size = 0
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
                        
                sizes[root] = total_size
                
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            
        return sizes
    
    def find_duplicate_files(self, directory: str, min_size: int = 1024) -> List[Tuple[str, List[str]]]:
        """Find duplicate files in directory."""
        file_hashes = {}
        duplicates = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Skip small files
                        if os.path.getsize(file_path) < min_size:
                            continue
                            
                        # Calculate file hash
                        file_hash = self._calculate_file_hash(file_path)
                        
                        if file_hash in file_hashes:
                            file_hashes[file_hash].append(file_path)
                        else:
                            file_hashes[file_hash] = [file_path]
                            
                    except (OSError, PermissionError, MemoryError):
                        continue
                        
            # Find duplicates
            for file_hash, paths in file_hashes.items():
                if len(paths) > 1:
                    duplicates.append((file_hash, paths))
                    self.cleanup_stats['duplicates_found'] += len(paths) - 1
                    
        except Exception as e:
            self.logger.error(f"Error finding duplicates: {e}")
            
        return duplicates
    
    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_sha256.update(chunk)
        except (OSError, MemoryError):
            return ""
            
        return hash_sha256.hexdigest()
    
    def remove_duplicates(self, duplicates: List[Tuple[str, List[str]]], keep_newest: bool = True) -> int:
        """Remove duplicate files, keeping specified version."""
        removed_count = 0
        
        for file_hash, paths in duplicates:
            if len(paths) <= 1:
                continue
                
            try:
                # Sort by modification time
                if keep_newest:
                    paths.sort(key=os.path.getmtime, reverse=True)
                else:
                    paths.sort(key=os.path.getmtime)
                    
                # Keep first file, remove rest
                for file_path in paths[1:]:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        self.cleanup_stats['space_freed'] += file_size
                        self.cleanup_stats['duplicates_removed'] += 1
                        self.cleanup_stats['files_removed'] += 1
                        removed_count += 1
                        self.logger.info(f"Removed duplicate: {file_path}")
                    except OSError as e:
                        self.logger.error(f"Failed to remove {file_path}: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error processing duplicates: {e}")
                
        return removed_count
    
    def clean_temp_files(self) -> Dict[str, int]:
        """Clean temporary files and caches."""
        cleaned = {
            'temp_files': 0,
            'cache_dirs': 0,
            'log_files': 0,
            'space_freed': 0
        }
        
        # Common temp directories
        temp_dirs = []
        
        if self.platform == 'windows':
            temp_dirs.extend([
                os.path.expandvars('%TEMP%'),
                os.path.expandvars('%TMP%'),
                os.path.expandvars('%LOCALAPPDATA%\\Temp')
            ])
        else:
            temp_dirs.extend([
                '/tmp',
                '/var/tmp',
                os.path.expanduser('~/.cache'),
                os.path.expanduser('~/.local/share/Trash')
            ])
        
        # Clean temp files
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                file_size = os.path.getsize(item_path)
                                os.remove(item_path)
                                cleaned['temp_files'] += 1
                                cleaned['space_freed'] += file_size
                                self.cleanup_stats['files_removed'] += 1
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                                cleaned['cache_dirs'] += 1
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError):
                    continue
        
        # Clean Python cache
        python_cache_dirs = []
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                python_cache_dirs.append(os.path.join(root, '__pycache__'))
                
        for cache_dir in python_cache_dirs:
            try:
                shutil.rmtree(cache_dir, ignore_errors=True)
                cleaned['cache_dirs'] += 1
                self.logger.info(f"Removed Python cache: {cache_dir}")
            except Exception as e:
                self.logger.error(f"Failed to remove cache {cache_dir}: {e}")
        
        return cleaned
    
    def clean_large_files(self, directory: str, max_size_mb: int = 100, 
                         file_types: List[str] = None) -> Dict[str, List[str]]:
        """Find and optionally remove large files."""
        if file_types is None:
            file_types = ['.log', '.tmp', '.bak', '.old']
            
        large_files = {'found': [], 'removed': []}
        max_size_bytes = max_size_mb * 1024 * 1024
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > max_size_bytes:
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in file_types:
                                large_files['found'].append((file_path, file_size))
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error scanning for large files: {e}")
            
        return large_files
    
    def optimize_disk_space(self, target_dir: str = '/') -> Dict[str, any]:
        """Comprehensive disk optimization."""
        results = {
            'initial_space': 0,
            'final_space': 0,
            'space_freed': 0,
            'operations': []
        }
        
        # Get initial space
        if PSUTIL_AVAILABLE:
            disk_usage = psutil.disk_usage(target_dir)
            results['initial_space'] = disk_usage.free
        
        try:
            # Operation 1: Clean temp files
            self.logger.info("Cleaning temporary files...")
            temp_results = self.clean_temp_files()
            results['operations'].append(f"Cleaned {temp_results['temp_files']} temp files")
            
            # Operation 2: Find duplicates in common directories
            self.logger.info("Scanning for duplicate files...")
            common_dirs = ['Downloads', 'Documents', 'Desktop', 'Pictures']
            
            for dir_name in common_dirs:
                dir_path = os.path.expanduser(f'~/{dir_name}')
                if os.path.exists(dir_path):
                    duplicates = self.find_duplicate_files(dir_path)
                    if duplicates:
                        removed = self.remove_duplicates(duplicates)
                        results['operations'].append(f"Removed {removed} duplicates from {dir_name}")
            
            # Operation 3: Clean large log files
            self.logger.info("Cleaning large log files...")
            large_logs = self.clean_large_files('.', max_size_mb=10, file_types=['.log'])
            for log_file, size in large_logs['found']:
                try:
                    os.remove(log_file)
                    self.cleanup_stats['space_freed'] += size
                    results['operations'].append(f"Removed large log: {log_file}")
                except OSError:
                    continue
            
            # Get final space
            if PSUTIL_AVAILABLE:
                disk_usage = psutil.disk_usage(target_dir)
                results['final_space'] = disk_usage.free
                results['space_freed'] = results['final_space'] - results['initial_space']
                
        except Exception as e:
            self.logger.error(f"Disk optimization failed: {e}")
            
        return results
    
    def get_disk_usage_report(self) -> Dict[str, any]:
        """Generate comprehensive disk usage report."""
        report = {
            'timestamp': time.time(),
            'system_info': self.get_system_info(),
            'disk_usage': {},
            'large_directories': {},
            'file_type_distribution': {},
            'recommendations': []
        }
        
        try:
            # Disk usage by mount point
            if PSUTIL_AVAILABLE:
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        report['disk_usage'][partition.mountpoint] = {
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': (usage.used / usage.total) * 100
                        }
                    except Exception:
                        continue
            
            # Large directories in home
            home_dir = os.path.expanduser('~')
            if os.path.exists(home_dir):
                dir_sizes = self.scan_directory_size(home_dir, max_depth=2)
                # Sort by size and take top 10
                sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
                report['large_directories'] = dict(sorted_dirs)
            
            # Generate recommendations
            if PSUTIL_AVAILABLE:
                for mount, usage in report['disk_usage'].items():
                    if usage['percent'] > 90:
                        report['recommendations'].append(f"Critical: {mount} is {usage['percent']:.1f}% full")
                    elif usage['percent'] > 80:
                        report['recommendations'].append(f"Warning: {mount} is {usage['percent']:.1f}% full")
                    elif usage['percent'] > 70:
                        report['recommendations'].append(f"Note: {mount} is {usage['percent']:.1f}% full")
                        
        except Exception as e:
            self.logger.error(f"Failed to generate disk report: {e}")
            
        return report
    
    def get_cleanup_summary(self) -> str:
        """Get summary of cleanup operations."""
        stats = self.cleanup_stats
        
        return f"""
System Helper Cleanup Summary:
📁 Files Removed: {stats['files_removed']}
💾 Space Freed: {stats['space_freed'] / (1024*1024):.1f} MB
🔍 Duplicates Found: {stats['duplicates_found']}
🗑️  Duplicates Removed: {stats['duplicates_removed']}
"""

class ScheduledTasks:
    """Scheduled system maintenance tasks."""
    
    def __init__(self, system_helper: SystemHelper):
        self.system_helper = system_helper
        self.logger = logging.getLogger('ScheduledTasks')
        self.task_history = []
        
    async def daily_cleanup(self):
        """Perform daily cleanup tasks."""
        self.logger.info("Starting daily cleanup...")
        
        try:
            results = self.system_helper.optimize_disk_space()
            
            self.task_history.append({
                'timestamp': time.time(),
                'task': 'daily_cleanup',
                'results': results
            })
            
            self.logger.info(f"Daily cleanup completed: {results['space_freed'] / (1024*1024):.1f} MB freed")
            
        except Exception as e:
            self.logger.error(f"Daily cleanup failed: {e}")
    
    async def weekly_scan(self):
        """Perform weekly system scan."""
        self.logger.info("Starting weekly system scan...")
        
        try:
            report = self.system_helper.get_disk_usage_report()
            
            self.task_history.append({
                'timestamp': time.time(),
                'task': 'weekly_scan',
                'results': report
            })
            
            # Log recommendations
            for rec in report.get('recommendations', []):
                self.logger.info(f"Recommendation: {rec}")
                
        except Exception as e:
            self.logger.error(f"Weekly scan failed: {e}")
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """Get recent task history."""
        return self.task_history[-limit:]

if __name__ == "__main__":
    # Test system helper
    logging.basicConfig(level=logging.INFO)
    
    helper = SystemHelper()
    
    print("System Information:")
    info = helper.get_system_info()
    print(f"Platform: {info.platform}")
    print(f"Memory: {info.memory_available / (1024**3):.1f} GB available")
    print(f"Disk: {info.disk_free / (1024**3):.1f} GB free")
    
    print("\nDisk Usage Report:")
    report = helper.get_disk_usage_report()
    for rec in report.get('recommendations', []):
        print(f"- {rec}")
    
    print("\n" + helper.get_cleanup_summary())
