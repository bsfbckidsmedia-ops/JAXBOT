#!/usr/bin/env python3
"""
Dual-Mode VRChat Bot
Can operate in VRChat mode or System Helper standby mode.
"""

import os
import sys
import asyncio
import logging
import signal
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

from dotenv import load_dotenv

# Import both modes
from main import VRChatBot, BotConfig
from minimal_main import MinimalVRChatBot
from system_helper import SystemHelper, ScheduledTasks

# Load environment variables
load_dotenv()

class BotMode(Enum):
    """Bot operating modes."""
    VRCHAT = "vrchat"
    STANDBY = "standby"
    SYSTEM_HELPER = "system_helper"
    MINIMAL_VRCHAT = "minimal_vrchat"

@dataclass
class DualModeConfig:
    """Configuration for dual-mode bot."""
    # VRChat settings
    vrc_username: str
    vrc_password: str
    vrc_bot_name: str = "DualBot"
    vrc_prefix: str = "!"
    
    # Mode settings
    default_mode: BotMode = BotMode.STANDBY
    auto_switch_modes: bool = True
    vrc_active_hours: str = "09:00-23:00"  # When to be active in VRChat
    
    # System helper settings
    enable_daily_cleanup: bool = True
    enable_weekly_scan: bool = True
    cleanup_time: str = "02:00"  # 2 AM cleanup
    scan_day: int = 0  # Sunday = 0
    
    # Resource limits
    max_memory_mb: int = 256
    max_storage_mb: int = 100
    
    # Monitoring
    health_check_interval: int = 300  # 5 minutes

class DualModeBot:
    """Dual-mode bot that can switch between VRChat and System Helper modes."""
    
    def __init__(self, config: DualModeConfig):
        self.config = config
        self.current_mode = config.default_mode
        self.running = False
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize components
        self.vrc_bot = None
        self.minimal_vrc_bot = None
        self.system_helper = SystemHelper()
        self.scheduled_tasks = ScheduledTasks(self.system_helper)
        
        # Mode switching state
        self.last_mode_switch = time.time()
        self.mode_switch_cooldown = 300  # 5 minutes
        
        # Health monitoring
        self.last_health_check = time.time()
        self.health_status = {
            'memory_ok': True,
            'storage_ok': True,
            'vrc_connected': False,
            'last_cleanup': 0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup dual-mode logging."""
        logger = logging.getLogger('DualModeBot')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler('dual_bot.log', mode='a')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        logger.addHandler(console_handler)
        
        return logger
    
    async def initialize(self):
        """Initialize bot components."""
        self.logger.info("Initializing Dual-Mode Bot...")
        
        # Initialize VRChat bot
        try:
            vrc_config = BotConfig(
                username=self.config.vrc_username,
                password=self.config.vrc_password,
                bot_name=self.config.vrc_bot_name,
                prefix=self.config.vrc_prefix,
                status="Dual-Mode Bot - Type !mode to switch modes",
                max_requests_per_minute=1,
                auto_reconnect=True,
                response_delay=2.0,
                max_memory_mb=self.config.max_memory_mb,
                max_storage_mb=self.config.max_storage_mb
            )
            self.vrc_bot = VRChatBot(vrc_config)
            self.logger.info("VRChat bot initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize VRChat bot: {e}")
        
        # Initialize minimal VRChat bot
        try:
            if os.getenv('VRCHAT_USERNAME') and os.getenv('VRCHAT_PASSWORD'):
                self.minimal_vrc_bot = MinimalVRChatBot()
                self.logger.info("Minimal VRChat bot initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize minimal VRChat bot: {e}")
        
        self.logger.info(f"Dual-Mode Bot initialized. Default mode: {self.current_mode.value}")
    
    def should_be_in_vrc_mode(self) -> bool:
        """Check if bot should be in VRChat mode based on time."""
        if not self.config.auto_switch_modes:
            return False
        
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Parse active hours (e.g., "09:00-23:00")
            start_hour, end_hour = map(int, self.config.vrc_active_hours.split('-'))
            
            return start_hour <= current_hour < end_hour
        except Exception:
            return False
    
    async def switch_mode(self, new_mode: BotMode, force: bool = False):
        """Switch to a different mode."""
        if not force and time.time() - self.last_mode_switch < self.mode_switch_cooldown:
            self.logger.warning("Mode switch cooldown active")
            return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.last_mode_switch = time.time()
        
        self.logger.info(f"Switching from {old_mode.value} to {new_mode.value}")
        
        # Stop current mode activities
        await self._stop_current_mode()
        
        # Start new mode activities
        await self._start_new_mode()
        
        return True
    
    async def _stop_current_mode(self):
        """Stop activities in current mode."""
        if self.current_mode in [BotMode.VRCHAT, BotMode.MINIMAL_VRCHAT]:
            # Stop VRChat activities
            if self.vrc_bot:
                self.vrc_bot.running = False
            if self.minimal_vrc_bot:
                self.minimal_vrc_bot.running = False
        
        # System helper mode doesn't need explicit stopping
        
    async def _start_new_mode(self):
        """Start activities in new mode."""
        if self.current_mode == BotMode.VRCHAT and self.vrc_bot:
            asyncio.create_task(self._run_vrc_bot())
        elif self.current_mode == BotMode.MINIMAL_VRCHAT and self.minimal_vrc_bot:
            asyncio.create_task(self._run_minimal_vrc_bot())
        elif self.current_mode == BotMode.SYSTEM_HELPER:
            asyncio.create_task(self._run_system_helper())
        elif self.current_mode == BotMode.STANDBY:
            asyncio.create_task(self._run_standby())
    
    async def _run_vrc_bot(self):
        """Run full VRChat bot."""
        try:
            self.logger.info("Starting VRChat mode (full)...")
            await self.vrc_bot.authenticate()
            await self.vrc_bot.monitor_friends()
        except Exception as e:
            self.logger.error(f"VRChat mode error: {e}")
    
    async def _run_minimal_vrc_bot(self):
        """Run minimal VRChat bot."""
        try:
            self.logger.info("Starting VRChat mode (minimal)...")
            await self.minimal_vrc_bot.authenticate()
            await self.minimal_vrc_bot.minimal_monitor()
        except Exception as e:
            self.logger.error(f"Minimal VRChat mode error: {e}")
    
    async def _run_system_helper(self):
        """Run system helper mode."""
        self.logger.info("Starting System Helper mode...")
        
        while self.running and self.current_mode == BotMode.SYSTEM_HELPER:
            try:
                # Perform system optimization
                results = self.system_helper.optimize_disk_space()
                
                if results['space_freed'] > 0:
                    self.logger.info(f"System Helper: Freed {results['space_freed'] / (1024*1024):.1f} MB")
                
                # Wait before next cycle
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                self.logger.error(f"System Helper error: {e}")
                await asyncio.sleep(60)
    
    async def _run_standby(self):
        """Run in standby mode with minimal activity."""
        self.logger.info("Starting Standby mode...")
        
        while self.running and self.current_mode == BotMode.STANDBY:
            try:
                # Check if should switch to VRChat mode
                if self.should_be_in_vrc_mode():
                    await self.switch_mode(BotMode.MINIMAL_VRCHAT)
                    continue
                
                # Perform light maintenance in standby
                if time.time() - self.health_status['last_cleanup'] > 3600:  # 1 hour
                    self.system_helper.clean_temp_files()
                    self.health_status['last_cleanup'] = time.time()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Standby mode error: {e}")
                await asyncio.sleep(60)
    
    async def health_check(self):
        """Perform health check and adjust mode if needed."""
        try:
            # Get system info
            system_info = self.system_helper.get_system_info()
            
            # Check memory
            memory_ok = system_info.memory_available > (100 * 1024 * 1024)  # 100MB
            self.health_status['memory_ok'] = memory_ok
            
            # Check storage
            storage_ok = system_info.disk_free > (50 * 1024 * 1024)  # 50MB
            self.health_status['storage_ok'] = storage_ok
            
            # Auto-adjust mode based on resources
            if not memory_ok or not storage_ok:
                if self.current_mode != BotMode.STANDBY:
                    self.logger.warning("Low resources, switching to standby mode")
                    await self.switch_mode(BotMode.STANDBY, force=True)
            
            self.last_health_check = time.time()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    async def run_scheduled_tasks(self):
        """Run scheduled maintenance tasks."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Daily cleanup at 2 AM
                if (self.config.enable_daily_cleanup and 
                    current_time.hour == 2 and current_time.minute == 0):
                    await self.scheduled_tasks.daily_cleanup()
                
                # Weekly scan on Sunday
                if (self.config.enable_weekly_scan and 
                    current_time.weekday() == self.config.scan_day and
                    current_time.hour == 3 and current_time.minute == 0):
                    await self.scheduled_tasks.weekly_scan()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Scheduled task error: {e}")
                await asyncio.sleep(300)
    
    def get_status(self) -> Dict:
        """Get current bot status."""
        return {
            'mode': self.current_mode.value,
            'running': self.running,
            'health': self.health_status,
            'uptime': time.time() - self.last_mode_switch,
            'system_info': self.system_helper.get_system_info().__dict__
        }
    
    async def run(self):
        """Main bot loop."""
        self.logger.info("Starting Dual-Mode Bot...")
        
        # Initialize components
        await self.initialize()
        
        if not self.vrc_bot and not self.minimal_vrc_bot:
            self.logger.error("No VRChat bot components initialized")
            return
        
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self.run_scheduled_tasks())
        
        # Start in default mode
        await self._start_new_mode()
        
        # Main monitoring loop
        try:
            while self.running:
                # Health check every 5 minutes
                if time.time() - self.last_health_check > self.config.health_check_interval:
                    await self.health_check()
                
                # Check for mode switches
                if self.config.auto_switch_modes:
                    should_be_vrc = self.should_be_in_vrc_mode()
                    is_vrc = self.current_mode in [BotMode.VRCHAT, BotMode.MINIMAL_VRCHAT]
                    
                    if should_be_vrc and not is_vrc:
                        await self.switch_mode(BotMode.MINIMAL_VRCHAT)
                    elif not should_be_vrc and is_vrc:
                        await self.switch_mode(BotMode.STANDBY)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal...")
        finally:
            self.running = False
            await self._stop_current_mode()
            self.logger.info("Dual-Mode Bot stopped.")

async def main():
    """Main entry point."""
    # Load configuration
    config = DualModeConfig(
        vrc_username=os.getenv('VRCHAT_USERNAME', ''),
        vrc_password=os.getenv('VRCHAT_PASSWORD', ''),
        vrc_bot_name=os.getenv('BOT_NAME', 'DualBot'),
        vrc_prefix=os.getenv('BOT_PREFIX', '!'),
        default_mode=BotMode(os.getenv('DEFAULT_MODE', 'standby')),
        auto_switch_modes=os.getenv('AUTO_SWITCH_MODES', 'true').lower() == 'true',
        vrc_active_hours=os.getenv('VRC_ACTIVE_HOURS', '09:00-23:00'),
        enable_daily_cleanup=os.getenv('ENABLE_DAILY_CLEANUP', 'true').lower() == 'true',
        enable_weekly_scan=os.getenv('ENABLE_WEEKLY_SCAN', 'true').lower() == 'true',
        max_memory_mb=int(os.getenv('MAX_MEMORY_MB', '256')),
        max_storage_mb=int(os.getenv('MAX_STORAGE_MB', '100'))
    )
    
    # Validate configuration
    if not config.vrc_username or not config.vrc_password:
        print("Error: VRCHAT_USERNAME and VRCHAT_PASSWORD must be set in .env file")
        sys.exit(1)
    
    # Create and run bot
    bot = DualModeBot(config)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        print("\nReceived signal, shutting down...")
        bot.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the bot
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
