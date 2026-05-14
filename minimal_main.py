#!/usr/bin/env python3
"""
Minimal VRChat Bot - Ultra Lightweight Version
Optimized for extremely resource-constrained environments.
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime

# Core imports only
import vrchatapi
from vrchatapi.api import authentication_api, friends_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from dotenv import load_dotenv
from chatbox import ChatBox
from tts import TTS

# Load environment variables from nano.env
load_dotenv('nano.env')

class MinimalVRChatBot:
    """Ultra-lightweight VRChat bot for resource-constrained systems."""
    
    def __init__(self):
        self.username = os.getenv('VRCHAT_USERNAME', '')
        self.password = os.getenv('VRCHAT_PASSWORD', '')
        self.bot_name = os.getenv('BOT_NAME', 'VRChatBot')
        self.prefix = os.getenv('BOT_PREFIX', '!')
        
        # Resource limits
        self.max_memory_mb = int(os.getenv('MAX_MEMORY_MB', '128'))  # Lowered for minimal version
        self.max_storage_mb = int(os.getenv('MAX_STORAGE_MB', '50'))   # Lowered for minimal version
        
        self.api_client = None
        self.auth_api = None
        self.friends_api = None
        self.current_user = None
        self.running = False
        self.request_count = 0
        self.last_request_time = None
        
        # ChatBox and TTS
        self.chatbox = ChatBox()
        self.tts = TTS()
        
        # Simple logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log', mode='a'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MinimalBot')
        
    async def check_resources(self):
        """Simple resource check."""
        try:
            import psutil
            import shutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss // (1024 * 1024)
            
            # Check storage in a cross-platform way
            storage_mb = shutil.disk_usage('.').free // (1024 * 1024)
            
            self.logger.info(f"Resources: Memory {memory_mb}MB, Storage {storage_mb}MB")
            
            # Emergency shutdown if critical
            if storage_mb < 30 or memory_mb > self.max_memory_mb:
                self.logger.critical("Critical resource shortage - shutting down")
                self.running = False
                return False
                
            return True
            
        except ImportError:
            # psutil not available, skip detailed monitoring
            return True
        except Exception as e:
            self.logger.error(f"Resource check failed: {e}")
            return True
    
    async def rate_limit(self):
        """Simple rate limiting."""
        current_time = time.time()
        
        if self.last_request_time is None:
            self.last_request_time = current_time
            return
            
        time_diff = current_time - self.last_request_time
        
        if time_diff < 60:  # Within last minute
            if self.request_count >= 1:  # VRChat limit
                wait_time = 60 - time_diff
                self.logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        else:
            self.request_count = 0
            self.last_request_time = time.time()
            
        self.request_count += 1
    
    async def authenticate(self):
        """Authenticate with VRChat."""
        try:
            self.logger.info("Authenticating...")
            
            configuration = vrchatapi.Configuration(
                username=self.username,
                password=self.password,
            )
            
            self.api_client = vrchatapi.ApiClient(configuration)
            self.api_client.user_agent = f"{self.bot_name}/1.0.0 https://github.com/username/vrchat-bot"
            
            self.auth_api = authentication_api.AuthenticationApi(self.api_client)
            self.friends_api = friends_api.FriendsApi(self.api_client)
            
            await self.rate_limit()
            
            try:
                self.current_user = self.auth_api.get_current_user()
            except UnauthorizedException as e:
                if e.status == 200:
                    if "Email 2 Factor Authentication" in e.reason:
                        code = os.getenv('VRCHAT_2FA_CODE')
                        if not code:
                            self.logger.error("Email 2FA required but not provided")
                            return False
                        self.auth_api.verify2_fa_email_code(
                            two_factor_email_code=TwoFactorEmailCode(code)
                        )
                    elif "2 Factor Authentication" in e.reason:
                        code = os.getenv('VRCHAT_2FA_CODE')
                        if not code:
                            self.logger.error("2FA required but not provided")
                            return False
                        self.auth_api.verify2_fa(
                            two_factor_auth_code=TwoFactorAuthCode(code)
                        )
                    else:
                        self.logger.error(f"Authentication failed: {e}")
                        return False
                    
                    self.current_user = self.auth_api.get_current_user()
                else:
                    raise
                    
            self.logger.info(f"Authenticated as: {self.current_user.display_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def process_command(self, message, sender):
        """Process simple commands. Responses are sent to ChatBox."""
        if not message.startswith(self.prefix):
            return None
            
        parts = message[len(self.prefix):].lower().strip().split()
        cmd = parts[0] if parts else ''
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == 'help':
            response = (
                f"{self.bot_name} Commands:\n"
                f"{self.prefix}help - Show help\n"
                f"{self.prefix}info - Bot info\n"
                f"{self.prefix}ping - Test\n"
                f"{self.prefix}say <text> - ChatBox + TTS\n"
                f"{self.prefix}tts <text> - TTS only\n"
                f"{self.prefix}chatbox <text> - ChatBox only"
            )
        elif cmd == 'info':
            response = f"{self.bot_name} - Lightweight VRChat Bot\nUser: {self.current_user.display_name if self.current_user else 'Unknown'}"
        elif cmd == 'ping':
            response = "Pong!"
        elif cmd == 'say':
            text = ' '.join(args) if args else 'Hello!'
            self.chatbox.send(text)
            self.tts.speak(text)
            response = f"Said: {text}"
        elif cmd == 'tts':
            text = ' '.join(args) if args else 'Hello!'
            self.tts.speak(text)
            response = f"TTS: {text}"
        elif cmd == 'chatbox':
            text = ' '.join(args) if args else 'Hello!'
            self.chatbox.send(text)
            response = f"ChatBox: {text}"
        else:
            response = "Unknown command. Use !help"
        
        self.chatbox.send(response)
        return response
    
    async def minimal_monitor(self):
        """Minimal friend monitoring."""
        self.logger.info("Starting minimal monitoring...")
        
        cycle_count = 0
        
        while self.running:
            try:
                # Resource check every 20 cycles (10 minutes)
                cycle_count += 1
                if cycle_count >= 20:
                    if not await self.check_resources():
                        break
                    cycle_count = 0
                
                await self.rate_limit()
                friends = self.friends_api.get_friends()
                
                online_count = sum(1 for f in friends if f.status == 'online')
                if online_count > 0:
                    self.logger.info(f"Online friends: {online_count}")
                
                # Simple cleanup
                if cycle_count % 50 == 0:  # Every ~25 minutes
                    self.cleanup_resources()
                
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def cleanup_resources(self):
        """Simple resource cleanup."""
        try:
            import gc
            gc.collect()
            
            # Clean log if too large
            if os.path.exists('bot.log'):
                size = os.path.getsize('bot.log')
                if size > 2 * 1024 * 1024:  # 2MB limit
                    with open('bot.log', 'w') as f:
                        f.write(f"Log cleaned at {datetime.now()}\n")
                    self.logger.info("Log cleaned")
                    
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    async def run(self):
        """Run the minimal bot."""
        self.logger.info(f"Starting {self.bot_name} (Minimal Version)")
        
        if not await self.authenticate():
            self.logger.error("Authentication failed")
            return
        
        self.running = True
        
        # Start ChatBox standby scrolling messages
        standby_messages = [
            f"{self.bot_name} | Online",
            f"Type {self.prefix}help for commands",
        ]
        await self.chatbox.start_scrolling(standby_messages, interval=5.0)
        
        try:
            await self.minimal_monitor()
        except KeyboardInterrupt:
            self.logger.info("Interrupt received")
        finally:
            await self.chatbox.stop_scrolling()
            self.chatbox.clear()
            self.running = False
            self.logger.info("Bot stopped")

def check_minimum_requirements():
    """Check if system meets minimum requirements."""
    try:
        import shutil
        storage_gb = shutil.disk_usage('.').free / (1024**3)
        print(f"Available storage: {storage_gb:.1f} GB")
        
        if storage_gb < 0.2:  # 200MB minimum
            print("WARNING: Very low storage space")
            return False
        
        return True
        
    except Exception as e:
        print(f"System check failed: {e}")
        return True  # Continue anyway

async def main():
    """Main entry point."""
    if not check_minimum_requirements():
        print("System does not meet minimum requirements")
        sys.exit(1)
    
    if not os.getenv('VRCHAT_USERNAME') or not os.getenv('VRCHAT_PASSWORD'):
        print("Error: VRCHAT_USERNAME and VRCHAT_PASSWORD must be set")
        sys.exit(1)
    
    bot = MinimalVRChatBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
