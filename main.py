#!/usr/bin/env python3
"""
VRChat Standalone Bot
A fully autonomous VRChat chatbot that can run without human intervention.
"""

import os
import sys
import asyncio
import logging
import signal
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

import vrchatapi
from vrchatapi.api import authentication_api, users_api, friends_api, worlds_api
from vrchatapi.exceptions import UnauthorizedException, ApiException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

import yaml
from dotenv import load_dotenv
from resource_monitor import ResourceMonitor, ResourceLimits, LightweightLogger

# Load environment variables from nano.env
load_dotenv('nano.env')

@dataclass
class BotConfig:
    """Configuration for the VRChat bot."""
    username: str
    password: str
    bot_name: str
    prefix: str
    status: str
    max_requests_per_minute: int
    auto_reconnect: bool
    response_delay: float
    max_memory_mb: int = 256
    max_storage_mb: int = 100

class VRChatBot:
    """Main VRChat bot class."""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.api_client = None
        self.auth_api = None
        self.users_api = None
        self.friends_api = None
        self.worlds_api = None
        self.current_user = None
        self.running = False
        self.last_request_time = None
        self.request_count = 0
        
        # Resource monitoring
        resource_limits = ResourceLimits(
            max_memory_mb=config.max_memory_mb,
            max_storage_mb=config.max_storage_mb
        )
        self.resource_monitor = ResourceMonitor(resource_limits)
        self.logger = self._setup_lightweight_logging()
        
        # Load responses from config
        self.responses = self._load_responses()
        
    def _setup_lightweight_logging(self) -> logging.Logger:
        """Setup lightweight logging for resource-constrained environments."""
        lightweight_logger = LightweightLogger(max_file_size_mb=3, max_files=2)
        logger = lightweight_logger.logger
        
        # Also add simple console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        
        return logger
        
    def _load_responses(self) -> Dict:
        """Load response patterns from config file."""
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                return config.get('responses', {})
        except Exception as e:
            self.logger.warning(f"Could not load responses from config: {e}")
            return {}
            
    async def _rate_limit(self):
        """Implement rate limiting to respect VRChat API limits."""
        if self.last_request_time is None:
            self.last_request_time = datetime.now()
            return
            
        time_diff = (datetime.now() - self.last_request_time).total_seconds()
        
        if time_diff < 60:  # Within the last minute
            if self.request_count >= self.config.max_requests_per_minute:
                wait_time = 60 - time_diff
                self.logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = datetime.now()
        else:
            # Reset counter if more than a minute has passed
            self.request_count = 0
            self.last_request_time = datetime.now()
            
        self.request_count += 1
        
    async def authenticate(self) -> bool:
        """Authenticate with VRChat API."""
        try:
            self.logger.info("Attempting to authenticate with VRChat...")
            
            # Setup configuration
            configuration = vrchatapi.Configuration(
                username=self.config.username,
                password=self.config.password,
            )
            
            # Create API client
            self.api_client = vrchatapi.ApiClient(configuration)
            self.api_client.user_agent = f"{self.config.bot_name}/1.0.0 https://github.com/username/vrchat-bot"
            
            # Create API instances
            self.auth_api = authentication_api.AuthenticationApi(self.api_client)
            self.users_api = users_api.UsersApi(self.api_client)
            self.friends_api = friends_api.FriendsApi(self.api_client)
            self.worlds_api = worlds_api.WorldsApi(self.api_client)
            
            await self._rate_limit()
            
            # Attempt to get current user (this logs in if not already)
            try:
                self.current_user = self.auth_api.get_current_user()
            except UnauthorizedException as e:
                if e.status == 200:
                    if "Email 2 Factor Authentication" in e.reason:
                        self.logger.info("Email 2FA required")
                        code = os.getenv('VRCHAT_2FA_CODE')
                        if not code:
                            self.logger.error("Email 2FA code required but not provided")
                            return False
                        self.auth_api.verify2_fa_email_code(
                            two_factor_email_code=TwoFactorEmailCode(code)
                        )
                    elif "2 Factor Authentication" in e.reason:
                        self.logger.info("2FA required")
                        code = os.getenv('VRCHAT_2FA_CODE')
                        if not code:
                            self.logger.error("2FA code required but not provided")
                            return False
                        self.auth_api.verify2_fa(
                            two_factor_auth_code=TwoFactorAuthCode(code)
                        )
                    else:
                        self.logger.error(f"Authentication failed: {e}")
                        return False
                    
                    # Retry getting current user after 2FA
                    self.current_user = self.auth_api.get_current_user()
                else:
                    raise
                    
            self.logger.info(f"Successfully authenticated as: {self.current_user.display_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
            
    async def update_status(self, status: str):
        """Update the bot's status message."""
        try:
            await self._rate_limit()
            # Note: Status update would require the appropriate API endpoint
            # This is a placeholder for the actual implementation
            self.logger.info(f"Status updated: {status}")
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
            
    def process_message(self, message: str, sender: str) -> Optional[str]:
        """Process incoming messages and generate responses."""
        message = message.strip()
        
        # Check if message is a command
        if message.startswith(self.config.prefix):
            return self.handle_command(message[len(self.config.prefix):], sender)
            
        # Check for greetings
        lower_message = message.lower()
        greetings = ['hello', 'hi', 'hey', 'greetings']
        if any(greeting in lower_message for greeting in greetings):
            return self._get_random_response('greetings')
            
        # Check for farewells
        farewells = ['goodbye', 'bye', 'see you', 'farewell']
        if any(farewell in lower_message for farewell in farewells):
            return self._get_random_response('farewells')
            
        return None
        
    def handle_command(self, command: str, sender: str) -> str:
        """Handle bot commands."""
        command = command.lower().strip()
        
        if command == 'help':
            return self._help_command()
        elif command == 'info':
            return self._info_command()
        elif command == 'status':
            return self._status_command()
        elif command == 'ping':
            return "Pong! 🏓"
        elif command == 'time':
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return self._get_random_response('unknown_commands')
            
    def _help_command(self) -> str:
        """Return help message."""
        return f"""{self.config.bot_name} Commands:
{self.config.prefix}help - Show this help message
{self.config.prefix}info - Show bot information
{self.config.prefix}status - Show current status
{self.config.prefix}ping - Test bot responsiveness
{self.config.prefix}time - Show current time

You can also greet me or say goodbye!"""
        
    def _info_command(self) -> str:
        """Return bot information."""
        return f"""{self.config.bot_name} - VRChat Assistant Bot
Version: 1.0.0
I'm a standalone VRChat bot that can run autonomously.
I can respond to commands and chat with users in VRChat."""
        
    def _status_command(self) -> str:
        """Return current status."""
        return f"Bot Status: Online | User: {self.current_user.display_name if self.current_user else 'Unknown'}"
        
    def _get_random_response(self, category: str) -> str:
        """Get a random response from a category."""
        import random
        responses = self.responses.get(category, ["I'm not sure how to respond to that."])
        return random.choice(responses)
        
    async def monitor_friends(self):
        """Monitor friend activities and respond to messages with resource management."""
        self.logger.info("Starting friend monitoring...")
        
        # Resource monitoring loop
        resource_check_counter = 0
        
        while self.running:
            try:
                # Check resources every 10 cycles (5 minutes)
                resource_check_counter += 1
                if resource_check_counter >= 10:
                    await self._check_and_cleanup_resources()
                    resource_check_counter = 0
                
                # Emergency shutdown check
                if self.resource_monitor.emergency_shutdown_check():
                    self.running = False
                    break
                
                await self._rate_limit()
                # Get friends list
                friends = self.friends_api.get_friends()
                
                # Check for online friends (placeholder for actual message monitoring)
                online_friends = [f for f in friends if f.status == 'online']
                if online_friends:
                    self.logger.info(f"Found {len(online_friends)} online friends")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in friend monitoring: {e}")
                if self.config.auto_reconnect:
                    self.logger.info("Attempting to reconnect...")
                    await asyncio.sleep(60)
                    await self.authenticate()
                else:
                    break
    
    async def _check_and_cleanup_resources(self):
        """Check resources and perform cleanup if needed."""
        try:
            status = self.resource_monitor.check_resources()
            
            # Log resource status
            self.logger.info(self.resource_monitor.get_runtime_stats())
            
            # Handle warnings
            for warning in status.get('warnings', []):
                self.logger.warning(f"Resource warning: {warning}")
                
            # Handle critical issues
            for critical in status.get('critical', []):
                self.logger.error(f"Resource critical: {critical}")
                
                # Perform cleanup if needed
                if 'memory' in critical.lower():
                    self.resource_monitor.optimize_memory()
                    self.resource_monitor.cleanup_logs()
                elif 'storage' in critical.lower():
                    self.resource_monitor.cleanup_logs()
                    self.resource_monitor.cleanup_cache()
                    
        except Exception as e:
            self.logger.error(f"Resource check failed: {e}")
                    
    async def run(self):
        """Main bot loop."""
        self.logger.info("Starting VRChat Bot...")
        
        # Authenticate
        if not await self.authenticate():
            self.logger.error("Failed to authenticate. Exiting...")
            return
            
        # Set initial status
        await self.update_status(self.config.status)
        
        self.running = True
        
        # Start monitoring
        try:
            await self.monitor_friends()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal...")
        finally:
            self.running = False
            self.logger.info("Bot stopped.")

async def main():
    """Main entry point."""
    # Load configuration
    config = BotConfig(
        username=os.getenv('VRCHAT_USERNAME', ''),
        password=os.getenv('VRCHAT_PASSWORD', ''),
        bot_name=os.getenv('BOT_NAME', 'VRChatBot'),
        prefix=os.getenv('BOT_PREFIX', '!'),
        status=os.getenv('BOT_STATUS', 'Hello! I\'m a VRChat assistant bot. Type !help for commands.'),
        max_requests_per_minute=int(os.getenv('MAX_REQUESTS_PER_MINUTE', '1')),
        auto_reconnect=os.getenv('AUTO_RECONNECT', 'true').lower() == 'true',
        response_delay=float(os.getenv('RESPONSE_DELAY', '2.0')),
        max_memory_mb=int(os.getenv('MAX_MEMORY_MB', '256')),
        max_storage_mb=int(os.getenv('MAX_STORAGE_MB', '100'))
    )
    
    # Validate configuration
    if not config.username or not config.password:
        print("Error: VRCHAT_USERNAME and VRCHAT_PASSWORD must be set in .env file")
        sys.exit(1)
        
    # Create and run bot
    bot = VRChatBot(config)
    
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
