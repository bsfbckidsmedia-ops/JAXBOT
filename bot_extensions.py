#!/usr/bin/env python3
"""
VRChat Bot Extensions
Additional functionality for the VRChat bot including advanced features.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class BotExtensions:
    """Extended functionality for VRChat bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}
        self.command_history = []
        self.timers = {}
        
    async def auto_greet(self, user_id: str, username: str):
        """Automatically greet users who come online."""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'username': username,
                'first_seen': datetime.now(),
                'last_greeted': None,
                'interaction_count': 0
            }
            
        user_info = self.user_data[user_id]
        
        # Greet if it's been more than an hour since last greeting
        if (user_info['last_greeted'] is None or 
            datetime.now() - user_info['last_greeted'] > timedelta(hours=1)):
            
            greeting = random.choice([
                f"Welcome back {username}! 👋",
                f"Hi {username}! Good to see you!",
                f"Hello {username}! How are you today?",
            ])
            
            await self.bot.send_message(greeting, target_user=user_id)
            user_info['last_greeted'] = datetime.now()
            
    async def schedule_reminder(self, user_id: str, message: str, delay_minutes: int):
        """Schedule a reminder for a user."""
        reminder_time = datetime.now() + timedelta(minutes=delay_minutes)
        
        if user_id not in self.timers:
            self.timers[user_id] = []
            
        self.timers[user_id].append({
            'message': message,
            'time': reminder_time,
            'sent': False
        })
        
        await self.bot.send_message(
            f"Reminder set: I'll remind you about '{message}' in {delay_minutes} minutes.",
            target_user=user_id
        )
        
    async def check_reminders(self):
        """Check and send any pending reminders."""
        current_time = datetime.now()
        
        for user_id, reminders in self.timers.items():
            for reminder in reminders:
                if not reminder['sent'] and current_time >= reminder['time']:
                    await self.bot.send_message(
                        f"⏰ Reminder: {reminder['message']}",
                        target_user=user_id
                    )
                    reminder['sent'] = True
                    
    async def log_interaction(self, user_id: str, command: str, response: str):
        """Log user interactions for analytics."""
        if user_id not in self.user_data:
            return
            
        self.user_data[user_id]['interaction_count'] += 1
        
        self.command_history.append({
            'timestamp': datetime.now(),
            'user_id': user_id,
            'command': command,
            'response': response[:100] + "..." if len(response) > 100 else response
        })
        
        # Keep only last 1000 commands in history
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]
            
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user."""
        if user_id not in self.user_data:
            return {}
            
        user_info = self.user_data[user_id]
        current_time = datetime.now()
        
        return {
            'username': user_info['username'],
            'first_seen': user_info['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
            'interaction_count': user_info['interaction_count'],
            'time_since_first_seen': str(current_time - user_info['first_seen']),
            'last_greeted': user_info['last_greeted'].strftime('%Y-%m-%d %H:%M:%S') if user_info['last_greeted'] else 'Never'
        }
        
    async def cleanup_old_data(self):
        """Clean up old user data and reminders."""
        cutoff_time = datetime.now() - timedelta(days=30)
        
        # Remove old user data
        old_users = [
            user_id for user_id, data in self.user_data.items()
            if data['first_seen'] < cutoff_time
        ]
        
        for user_id in old_users:
            del self.user_data[user_id]
            
        # Remove old sent reminders
        for user_id in list(self.timers.keys()):
            self.timers[user_id] = [
                reminder for reminder in self.timers[user_id]
                if not reminder['sent'] or reminder['time'] > cutoff_time
            ]
            
            if not self.timers[user_id]:
                del self.timers[user_id]

class AdvancedCommands:
    """Advanced command handlers for the bot."""
    
    def __init__(self, bot, extensions):
        self.bot = bot
        self.extensions = extensions
        
    async def handle_reminder(self, args: List[str], sender: str) -> str:
        """Handle reminder commands."""
        if len(args) < 2:
            return "Usage: !reminder <minutes> <message>"
            
        try:
            minutes = int(args[0])
            message = " ".join(args[1:])
            
            await self.extensions.schedule_reminder(sender, message, minutes)
            return f"Reminder scheduled for {minutes} minutes from now."
            
        except ValueError:
            return "Invalid time format. Usage: !reminder <minutes> <message>"
            
    async def handle_stats(self, args: List[str], sender: str) -> str:
        """Handle stats commands."""
        if args and args[0].lower() == 'bot':
            return self._get_bot_stats()
        else:
            stats = self.extensions.get_user_stats(sender)
            if not stats:
                return "No statistics available for you yet."
                
            return f"""Your Statistics:
📊 Interactions: {stats['interaction_count']}
🕐 First seen: {stats['first_seen']}
⏱️ Time since first seen: {stats['time_since_first_seen']}
👋 Last greeted: {stats['last_greeted']}"""
                
    def _get_bot_stats(self) -> str:
        """Get overall bot statistics."""
        total_users = len(self.extensions.user_data)
        total_interactions = sum(
            data['interaction_count'] 
            for data in self.extensions.user_data.values()
        )
        
        return f"""Bot Statistics:
👥 Total users: {total_users}
💬 Total interactions: {total_interactions}
📈 Commands in history: {len(self.extensions.command_history)}
⏰ Active reminders: {sum(len(reminders) for reminders in self.extensions.timers.values())}"""
        
    async def handle_joke(self, args: List[str], sender: str) -> str:
        """Tell a random joke."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the coffee file a police report? It got mugged!"
        ]
        
        return random.choice(jokes)
        
    async def handle_8ball(self, args: List[str], sender: str) -> str:
        """Magic 8-ball command."""
        if not args:
            return "Ask me a question! Usage: !8ball <question>"
            
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes, definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
            "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        
        return f"🎱 {random.choice(responses)}"

# Integration class to extend the main bot
class BotWithExtensions:
    """Main bot class with extensions integrated."""
    
    def __init__(self, config):
        from main import VRChatBot
        
        self.base_bot = VRChatBot(config)
        self.extensions = BotExtensions(self.base_bot)
        self.advanced_commands = AdvancedCommands(self.base_bot, self.extensions)
        
        # Override the handle_command method
        original_handle_command = self.base_bot.handle_command
        
        def extended_handle_command(command: str, sender: str) -> str:
            parts = command.lower().strip().split()
            cmd = parts[0] if parts else ""
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle extended commands
            if cmd == 'reminder':
                return asyncio.run(self.advanced_commands.handle_reminder(args, sender))
            elif cmd == 'stats':
                return asyncio.run(self.advanced_commands.handle_stats(args, sender))
            elif cmd == 'joke':
                return asyncio.run(self.advanced_commands.handle_joke(args, sender))
            elif cmd == '8ball':
                return asyncio.run(self.advanced_commands.handle_8ball(args, sender))
            else:
                # Use original command handler
                return original_handle_command(command, sender)
                
        self.base_bot.handle_command = extended_handle_command
        
        # Override monitor_friends to include extensions
        original_monitor = self.base_bot.monitor_friends
        
        async def extended_monitor_friends():
            await original_monitor()
            # Add extension-specific monitoring here
            await self.extensions.check_reminders()
            await self.extensions.cleanup_old_data()
            
        self.base_bot.monitor_friends = extended_monitor_friends
        
    async def run(self):
        """Run the extended bot."""
        await self.base_bot.run()
