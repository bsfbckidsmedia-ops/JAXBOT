#!/usr/bin/env python3
"""
GenAI Mode Module
Provides optional AI-powered responses using low-cost, low-resource GenAI providers.
"""

import logging
import os
import asyncio
import psutil
from typing import Optional, Dict, Any
from enum import Enum
import json

class GenAIProvider(Enum):
    """Supported GenAI providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GROQ = "groq"
    DISABLED = "disabled"

class GenAIMode:
    """GenAI mode for AI-powered bot responses."""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.enabled = config.get('enabled', False)
        self.provider = GenAIProvider(config.get('provider', 'disabled'))
        self.model = config.get('model', '')
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        self.max_tokens = config.get('max_tokens', 100)
        self.temperature = config.get('temperature', 0.7)
        
        # System prompt for the bot
        self.system_prompt = config.get(
            'system_prompt',
            "You are a helpful VRChat event assistant bot. Keep responses brief, friendly, and under 100 words. You help enforce event rules and assist users."
        )
        
        # Resource monitoring settings
        self.min_memory_mb = config.get('min_memory_mb', 100)  # Minimum free memory in MB
        self.resource_check_enabled = config.get('resource_check_enabled', True)
        
        # Initialize the provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected GenAI provider."""
        if not self.enabled or self.provider == GenAIProvider.DISABLED:
            self.logger.info("GenAI mode is disabled")
            return
        
        try:
            if self.provider == GenAIProvider.OLLAMA:
                self._init_ollama()
            elif self.provider == GenAIProvider.OPENAI:
                self._init_openai()
            elif self.provider == GenAIProvider.GROQ:
                self._init_groq()
            
            self.logger.info(f"GenAI mode initialized with provider: {self.provider.value}")
        except Exception as e:
            self.logger.error(f"Failed to initialize GenAI provider: {e}")
            self.enabled = False
    
    def _init_ollama(self):
        """Initialize Ollama (local, free)."""
        try:
            import requests
            self.requests = requests
            self.ollama_url = self.base_url or 'http://localhost:11434/api/generate'
            self.logger.info(f"Ollama initialized with model: {self.model}")
        except ImportError:
            self.logger.error("Requests library not installed. Install with: pip install requests")
            raise
        except Exception as e:
            self.logger.error(f"Ollama initialization failed: {e}")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI API (gpt-4o-mini - very cheap)."""
        try:
            import openai
            self.openai = openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            if not self.model:
                self.model = "gpt-4o-mini"  # Very cheap and fast
            self.logger.info(f"OpenAI initialized with model: {self.model}")
        except ImportError:
            self.logger.error("OpenAI library not installed. Install with: pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"OpenAI initialization failed: {e}")
            raise
    
    def _init_groq(self):
        """Initialize Groq API (very fast and cheap)."""
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=self.api_key)
            if not self.model:
                self.model = "llama-3.2-3b-preview"  # Small, fast, cheap
            self.logger.info(f"Groq initialized with model: {self.model}")
        except ImportError:
            self.logger.error("Groq library not installed. Install with: pip install groq")
            raise
        except Exception as e:
            self.logger.error(f"Groq initialization failed: {e}")
            raise
    
    def _check_resources(self) -> bool:
        """Check if system has sufficient resources for GenAI."""
        if not self.resource_check_enabled:
            return True
        
        try:
            # Check available memory
            mem = psutil.virtual_memory()
            available_mb = mem.available / (1024 * 1024)
            
            if available_mb < self.min_memory_mb:
                self.logger.warning(
                    f"Insufficient memory for GenAI: {available_mb:.1f}MB available, "
                    f"{self.min_memory_mb}MB required"
                )
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Resource check failed: {e}")
            # Allow generation if check fails
            return True
    
    async def generate_response(self, message: str, sender: str, context: Optional[str] = None) -> Optional[str]:
        """
        Generate an AI response to a message.
        
        Args:
            message: The user's message
            sender: The username of the sender
            context: Optional context about the conversation
            
        Returns:
            AI-generated response or None if disabled/error
        """
        if not self.enabled:
            return None
        
        # Check resources before generation
        if not self._check_resources():
            self.logger.warning("Skipping GenAI generation due to insufficient resources")
            return None
        
        try:
            if self.provider == GenAIProvider.OLLAMA:
                return await self._generate_ollama(message, sender, context)
            elif self.provider == GenAIProvider.OPENAI:
                return await self._generate_openai(message, sender, context)
            elif self.provider == GenAIProvider.GROQ:
                return await self._generate_groq(message, sender, context)
            
            return None
        except Exception as e:
            self.logger.error(f"GenAI generation failed: {e}")
            return None
    
    async def _generate_ollama(self, message: str, sender: str, context: Optional[str]) -> str:
        """Generate response using Ollama."""
        prompt = self._build_prompt(message, sender, context)
        
        try:
            response = self.requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": self.max_tokens,
                        "temperature": self.temperature
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            raise
    
    async def _generate_openai(self, message: str, sender: str, context: Optional[str]) -> str:
        """Generate response using OpenAI."""
        prompt = self._build_prompt(message, sender, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def _generate_groq(self, message: str, sender: str, context: Optional[str]) -> str:
        """Generate response using Groq."""
        prompt = self._build_prompt(message, sender, context)
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Groq generation error: {e}")
            raise
    
    def _build_prompt(self, message: str, sender: str, context: Optional[str]) -> str:
        """Build the prompt for the AI."""
        base_prompt = f"User: {sender}\nMessage: {message}\n"
        if context:
            base_prompt += f"Context: {context}\n"
        base_prompt += "Response:"
        return base_prompt
    
    def toggle(self, enabled: bool):
        """Toggle GenAI mode on/off."""
        self.enabled = enabled
        if enabled:
            self._initialize_provider()
        self.logger.info(f"GenAI mode {'enabled' if enabled else 'disabled'}")
    
    def is_enabled(self) -> bool:
        """Check if GenAI mode is enabled."""
        return self.enabled
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            'enabled': self.enabled,
            'provider': self.provider.value if self.enabled else 'disabled',
            'model': self.model if self.enabled else '',
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
    
    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
        self.logger.info(f"Model changed to: {model}")
        # Reinitialize if needed
        if self.enabled:
            self._initialize_provider()
