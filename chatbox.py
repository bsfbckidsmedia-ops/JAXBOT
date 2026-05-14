#!/usr/bin/env python3
"""
VRChat ChatBox Module
Sends text to VRChat's in-world ChatBox via OSC protocol.
Supports direct messaging, typing indicators, and scrolling messages.
"""

import asyncio
import logging
import time
from typing import Optional

from pythonosc.udp_client import SimpleUDPClient

logger = logging.getLogger(__name__)

# VRChat OSC defaults
DEFAULT_OSC_HOST = "127.0.0.1"
DEFAULT_OSC_PORT = 9000

# ChatBox limits
CHATBOX_MAX_LENGTH = 144
SCROLL_DEFAULT_INTERVAL = 3.0
SCROLL_DEFAULT_WINDOW = 144


class ChatBox:
    """Interface to VRChat's OSC ChatBox."""

    def __init__(
        self,
        host: str = DEFAULT_OSC_HOST,
        port: int = DEFAULT_OSC_PORT,
    ):
        self.client = SimpleUDPClient(host, port)
        self._scroll_task: Optional[asyncio.Task] = None
        self._scroll_running = False

    def send(self, text: str, direct: bool = True, sound: bool = True):
        """Send a message to the ChatBox.

        Args:
            text: Message to display (max 144 chars, truncated if longer).
            direct: True to show immediately, False to fill the input field.
            sound: Play notification sound when message appears.
        """
        text = text[:CHATBOX_MAX_LENGTH]
        self.client.send_message("/chatbox/input", [text, direct, sound])
        logger.debug("ChatBox send: %s", text)

    def set_typing(self, is_typing: bool):
        """Toggle the typing indicator above the avatar."""
        self.client.send_message("/chatbox/typing", [is_typing])

    def clear(self):
        """Clear the ChatBox by sending an empty string."""
        self.client.send_message("/chatbox/input", ["", True, False])

    # --- scrolling messages ---------------------------------------------------

    async def start_scrolling(
        self,
        messages: list[str],
        interval: float = SCROLL_DEFAULT_INTERVAL,
        loop: bool = True,
    ):
        """Cycle through a list of messages in the ChatBox.

        Args:
            messages: Texts to rotate through.
            interval: Seconds between each message.
            loop: Repeat after reaching the end.
        """
        await self.stop_scrolling()
        self._scroll_running = True
        self._scroll_task = asyncio.create_task(
            self._scroll_loop(messages, interval, loop)
        )

    async def stop_scrolling(self):
        """Stop the current scrolling message loop."""
        self._scroll_running = False
        if self._scroll_task and not self._scroll_task.done():
            self._scroll_task.cancel()
            try:
                await self._scroll_task
            except asyncio.CancelledError:
                pass
        self._scroll_task = None

    async def _scroll_loop(
        self, messages: list[str], interval: float, loop: bool
    ):
        """Internal coroutine that drives the scrolling display."""
        idx = 0
        while self._scroll_running:
            if idx >= len(messages):
                if loop:
                    idx = 0
                else:
                    break
            self.send(messages[idx], direct=True, sound=False)
            idx += 1
            await asyncio.sleep(interval)
        self.clear()

    @property
    def is_scrolling(self) -> bool:
        return self._scroll_running and self._scroll_task is not None
