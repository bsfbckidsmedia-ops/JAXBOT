#!/usr/bin/env python3
"""
Text-to-Speech Module
Lightweight offline TTS using pyttsx3 (espeak / SAPI5 / nsss backend).
"""

import logging
import os
from typing import Optional

import pyttsx3

logger = logging.getLogger(__name__)

DEFAULT_RATE = 150
DEFAULT_VOLUME = 1.0


class TTS:
    """Offline text-to-speech wrapper around pyttsx3."""

    def __init__(
        self,
        rate: int = DEFAULT_RATE,
        volume: float = DEFAULT_VOLUME,
        voice_id: Optional[str] = None,
    ):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        if voice_id:
            self.engine.setProperty("voice", voice_id)

    def speak(self, text: str):
        """Speak text aloud through the default audio output."""
        logger.debug("TTS speak: %s", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def save(self, text: str, filepath: str = "output.wav"):
        """Render speech to an audio file."""
        logger.debug("TTS save: %s -> %s", text, filepath)
        self.engine.save_to_file(text, filepath)
        self.engine.runAndWait()

    def list_voices(self) -> list[dict]:
        """Return available voices on this system."""
        voices = self.engine.getProperty("voices")
        return [
            {"id": v.id, "name": v.name, "languages": v.languages}
            for v in voices
        ]

    def set_voice(self, voice_id: str):
        """Switch to a specific voice by ID."""
        self.engine.setProperty("voice", voice_id)

    def set_rate(self, rate: int):
        """Set speech rate (words per minute)."""
        self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self.engine.setProperty("volume", max(0.0, min(1.0, volume)))
