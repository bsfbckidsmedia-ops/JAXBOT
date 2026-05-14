#!/usr/bin/env python3
"""
JaxBot Console
Interactive console launcher that wraps MinimalVRChatBot with ChatBox and TTS.
Provides a command-line interface for controlling the bot at startup and runtime.
"""

import os
import sys
import asyncio
import signal
import threading
from datetime import datetime

from dotenv import load_dotenv

from minimal_main import MinimalVRChatBot, check_minimum_requirements
from chatbox import ChatBox
from tts import TTS

BANNER = r"""
     ██╗ █████╗ ██╗  ██╗██████╗  ██████╗ ████████╗
     ██║██╔══██╗╚██╗██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
     ██║███████║ ╚███╔╝ ██████╔╝██║   ██║   ██║
██   ██║██╔══██║ ██╔██╗ ██╔══██╗██║   ██║   ██║
╚█████╔╝██║  ██║██╔╝ ██╗██████╔╝╚██████╔╝   ██║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝
       VRChat ChatBox & TTS Standby Bot
"""

HELP_TEXT = """
=== JaxBot Console Commands ===

  start         - Start the bot (authenticate & begin monitoring)
  stop          - Stop the bot gracefully
  status        - Show bot status
  chatbox <msg> - Send a message to the VRChat ChatBox
  tts <msg>     - Speak a message via text-to-speech
  say <msg>     - Send to ChatBox AND speak via TTS
  scroll <msgs> - Set scrolling messages (comma-separated)
  scroll stop   - Stop scrolling messages
  voices        - List available TTS voices
  voice <id>    - Set TTS voice by ID
  rate <wpm>    - Set TTS speech rate (words per minute)
  volume <0-1>  - Set TTS volume
  clear         - Clear the ChatBox
  config        - Show current configuration
  help          - Show this help message
  quit / exit   - Shut down and exit

"""


class JaxBotConsole:
    """Interactive console for controlling JaxBot."""

    def __init__(self):
        # Load env before creating bot
        load_dotenv('nano.env')

        self.bot = None
        self.chatbox = ChatBox()
        self.tts = TTS()
        self.bot_task = None
        self.running = True

    # ---- helpers ----

    def _print(self, msg: str):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def _bot_running(self) -> bool:
        return self.bot is not None and self.bot.running

    # ---- console commands ----

    async def cmd_start(self, _args: str):
        if self._bot_running():
            self._print("Bot is already running.")
            return

        username = os.getenv('VRCHAT_USERNAME', '')
        password = os.getenv('VRCHAT_PASSWORD', '')

        if not username or not password:
            self._print("ERROR: VRCHAT_USERNAME and VRCHAT_PASSWORD must be set in nano.env")
            return

        self._print("Starting bot...")
        self.bot = MinimalVRChatBot()
        # Share the console's ChatBox/TTS instances
        self.bot.chatbox = self.chatbox
        self.bot.tts = self.tts

        self.bot_task = asyncio.create_task(self._run_bot())

    async def _run_bot(self):
        try:
            await self.bot.run()
        except Exception as e:
            self._print(f"Bot error: {e}")
        finally:
            self._print("Bot has stopped.")

    async def cmd_stop(self, _args: str):
        if not self._bot_running():
            self._print("Bot is not running.")
            return
        self._print("Stopping bot...")
        self.bot.running = False
        await self.chatbox.stop_scrolling()
        self.chatbox.clear()

    async def cmd_status(self, _args: str):
        if self._bot_running():
            user = self.bot.current_user
            name = user.display_name if user else "authenticating..."
            self._print(f"Bot: RUNNING | User: {name}")
            self._print(f"ChatBox scrolling: {self.chatbox.is_scrolling}")
        else:
            self._print("Bot: STOPPED")

    async def cmd_chatbox(self, args: str):
        text = args.strip() or "Hello from JaxBot!"
        self.chatbox.send(text)
        self._print(f"ChatBox -> {text}")

    async def cmd_tts(self, args: str):
        text = args.strip() or "Hello from JaxBot!"
        self._print(f"TTS -> {text}")
        self.tts.speak(text)

    async def cmd_say(self, args: str):
        text = args.strip() or "Hello from JaxBot!"
        self.chatbox.send(text)
        self._print(f"Say -> {text}")
        self.tts.speak(text)

    async def cmd_scroll(self, args: str):
        stripped = args.strip()
        if stripped.lower() == 'stop':
            await self.chatbox.stop_scrolling()
            self._print("Scrolling stopped.")
            return
        if not stripped:
            self._print("Usage: scroll <msg1>, <msg2>, ... OR scroll stop")
            return
        messages = [m.strip() for m in stripped.split(',') if m.strip()]
        await self.chatbox.start_scrolling(messages, interval=5.0)
        self._print(f"Scrolling {len(messages)} message(s).")

    async def cmd_voices(self, _args: str):
        voices = self.tts.list_voices()
        self._print(f"Available voices ({len(voices)}):")
        for v in voices:
            print(f"    {v['id']}  -  {v['name']}")

    async def cmd_voice(self, args: str):
        voice_id = args.strip()
        if not voice_id:
            self._print("Usage: voice <voice_id>")
            return
        self.tts.set_voice(voice_id)
        self._print(f"Voice set to: {voice_id}")

    async def cmd_rate(self, args: str):
        try:
            rate = int(args.strip())
            self.tts.set_rate(rate)
            self._print(f"TTS rate set to {rate} WPM")
        except ValueError:
            self._print("Usage: rate <number>")

    async def cmd_volume(self, args: str):
        try:
            vol = float(args.strip())
            self.tts.set_volume(vol)
            self._print(f"TTS volume set to {vol}")
        except ValueError:
            self._print("Usage: volume <0.0 - 1.0>")

    async def cmd_clear(self, _args: str):
        self.chatbox.clear()
        self._print("ChatBox cleared.")

    async def cmd_config(self, _args: str):
        self._print("Current configuration (nano.env):")
        for key in [
            'VRCHAT_USERNAME', 'BOT_NAME', 'BOT_PREFIX',
            'BOT_STATUS', 'MAX_REQUESTS_PER_MINUTE',
            'AUTO_RECONNECT', 'MAX_MEMORY_MB', 'MAX_STORAGE_MB',
        ]:
            val = os.getenv(key, '<not set>')
            print(f"    {key} = {val}")

    async def cmd_help(self, _args: str):
        print(HELP_TEXT)

    # ---- main loop ----

    COMMANDS = {
        'start': 'cmd_start',
        'stop': 'cmd_stop',
        'status': 'cmd_status',
        'chatbox': 'cmd_chatbox',
        'tts': 'cmd_tts',
        'say': 'cmd_say',
        'scroll': 'cmd_scroll',
        'voices': 'cmd_voices',
        'voice': 'cmd_voice',
        'rate': 'cmd_rate',
        'volume': 'cmd_volume',
        'clear': 'cmd_clear',
        'config': 'cmd_config',
        'help': 'cmd_help',
    }

    async def input_loop(self):
        """Read user input in a thread so we don't block the event loop."""
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                line = await loop.run_in_executor(
                    None, lambda: input("\n  jaxbot> ")
                )
            except (EOFError, KeyboardInterrupt):
                break

            line = line.strip()
            if not line:
                continue

            parts = line.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''

            if cmd in ('quit', 'exit'):
                await self.cmd_stop('')
                self.running = False
                break

            handler_name = self.COMMANDS.get(cmd)
            if handler_name:
                handler = getattr(self, handler_name)
                await handler(args)
            else:
                self._print(f"Unknown command: {cmd}. Type 'help' for a list.")

    async def run(self):
        print(BANNER)
        print("  Type 'help' for available commands, 'start' to launch the bot.\n")

        # Handle Ctrl+C
        def _signal_handler(sig, frame):
            self.running = False
            if self.bot:
                self.bot.running = False

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        await self.input_loop()

        # Cleanup
        if self._bot_running():
            self.bot.running = False
        await self.chatbox.stop_scrolling()
        self.chatbox.clear()
        self._print("Goodbye!")


def main():
    if not check_minimum_requirements():
        print("System does not meet minimum requirements.")
        sys.exit(1)

    console = JaxBotConsole()
    asyncio.run(console.run())


if __name__ == "__main__":
    main()
