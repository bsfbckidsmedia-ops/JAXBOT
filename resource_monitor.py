#!/usr/bin/env python3
"""
Resource Monitor for VRChat Bot
Monitors and manages system resources for low-resource environments.
"""

import os
import sys
import time
import shutil
import logging
from typing import Dict, Optional
from dataclasses import dataclass
import psutil
from pathlib import Path

@dataclass
class ResourceLimits:
    """Resource limits for the bot."""
    max_memory_mb: int = 512  # Maximum memory usage in MB
    max_storage_mb: int = 100  # Maximum storage usage in MB
    max_cpu_percent: float = 25.0  # Maximum CPU usage percentage
    cleanup_threshold_mb: int = 50  # When to start cleanup
    
class ResourceMonitor:
    """Monitor and manage system resources."""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.logger = logging.getLogger('ResourceMonitor')
        self.start_time = time.time()
        self.initial_storage = self._get_storage_info()['free_mb']
        
    def _get_storage_info(self) -> Dict:
        """Get storage information for the current directory."""
        import shutil
        total, used, free = shutil.disk_usage('.')
        total_mb = total // (1024 * 1024)
        free_mb = free // (1024 * 1024)
        used_mb = used // (1024 * 1024)
        
        return {
            'total_mb': total_mb,
            'free_mb': free_mb,
            'used_mb': used_mb,
            'free_percent': (free / total) * 100
        }
        
    def _get_memory_info(self) -> Dict:
        """Get memory information for the current process."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss // (1024 * 1024),
            'vms_mb': memory_info.vms // (1024 * 1024),
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available // (1024 * 1024)
        }
        
    def _get_cpu_info(self) -> Dict:
        """Get CPU information."""
        process = psutil.Process()
        
        return {
            'percent': process.cpu_percent(),
            'system_percent': psutil.cpu_percent(interval=1)
        }
        
    def check_resources(self) -> Dict:
        """Check all resources and return status."""
        storage = self._get_storage_info()
        memory = self._get_memory_info()
        cpu = self._get_cpu_info()
        
        status = {
            'storage': storage,
            'memory': memory,
            'cpu': cpu,
            'warnings': [],
            'critical': []
        }
        
        # Check storage
        if storage['free_mb'] < self.limits.max_storage_mb:
            status['critical'].append(f"Low storage: {storage['free_mb']}MB free")
        elif storage['free_mb'] < self.limits.cleanup_threshold_mb:
            status['warnings'].append(f"Storage cleanup needed: {storage['free_mb']}MB free")
            
        # Check memory
        if memory['rss_mb'] > self.limits.max_memory_mb:
            status['critical'].append(f"High memory usage: {memory['rss_mb']}MB")
        elif memory['rss_mb'] > self.limits.max_memory_mb * 0.8:
            status['warnings'].append(f"Memory usage high: {memory['rss_mb']}MB")
            
        # Check CPU
        if cpu['percent'] > self.limits.max_cpu_percent:
            status['warnings'].append(f"High CPU usage: {cpu['percent']:.1f}%")
            
        return status
        
    def cleanup_logs(self, max_log_size_mb: int = 10):
        """Clean up log files to save storage."""
        log_files = list(Path('.').glob('*.log'))
        total_size = sum(f.stat().st_size for f in log_files) // (1024 * 1024)
        
        if total_size > max_log_size_mb:
            self.logger.info(f"Cleaning up logs ({total_size}MB > {max_log_size_mb}MB)")
            
            for log_file in log_files:
                try:
                    # Truncate large log files
                    if log_file.stat().st_size > 5 * 1024 * 1024:  # 5MB
                        with open(log_file, 'w') as f:
                            f.write(f"Log truncated at {time.ctime()}\n")
                        self.logger.info(f"Truncated {log_file}")
                except Exception as e:
                    self.logger.error(f"Failed to clean {log_file}: {e}")
                    
    def cleanup_cache(self):
        """Clean up cache files and temporary data."""
        cache_dirs = ['__pycache__', '.pytest_cache', '.mypy_cache']
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    self.logger.info(f"Removed cache directory: {cache_dir}")
                except Exception as e:
                    self.logger.error(f"Failed to remove {cache_dir}: {e}")
                    
        # Clean up old temporary files
        temp_files = list(Path('.').glob('*.tmp'))
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                self.logger.info(f"Removed temp file: {temp_file}")
            except Exception as e:
                self.logger.error(f"Failed to remove {temp_file}: {e}")
                
    def optimize_memory(self):
        """Force garbage collection and memory optimization."""
        import gc
        
        # Force garbage collection
        collected = gc.collect()
        self.logger.info(f"Garbage collection: {collected} objects collected")
        
        # Clear module cache if memory is high
        memory_info = self._get_memory_info()
        if memory_info['rss_mb'] > self.limits.max_memory_mb * 0.8:
            # Clear some module caches
            if 'sys' in sys.modules:
                sys.modules.clear()
            self.logger.info("Cleared module cache for memory optimization")
            
    def get_runtime_stats(self) -> str:
        """Get runtime statistics."""
        runtime = time.time() - self.start_time
        hours = int(runtime // 3600)
        minutes = int((runtime % 3600) // 60)
        seconds = int(runtime % 60)
        
        storage = self._get_storage_info()
        memory = self._get_memory_info()
        
        return (f"Runtime: {hours:02d}:{minutes:02d}:{seconds:02d} | "
                f"Storage: {storage['free_mb']}MB free | "
                f"Memory: {memory['rss_mb']}MB used | "
                f"Available: {memory['available_mb']}MB")
                
    def emergency_shutdown_check(self) -> bool:
        """Check if emergency shutdown is needed."""
        storage = self._get_storage_info()
        
        # Emergency shutdown if less than 50MB free
        if storage['free_mb'] < 50:
            self.logger.critical(f"EMERGENCY: Critical storage ({storage['free_mb']}MB). Shutting down.")
            return True
            
        return False

class LightweightLogger:
    """Lightweight logging with rotation for low-resource environments."""
    
    def __init__(self, max_file_size_mb: int = 5, max_files: int = 2):
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_files = max_files
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup lightweight logger."""
        logger = logging.getLogger('VRChatBot')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            
        # Create simple file handler
        handler = logging.FileHandler('bot.log', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
        return logger
        
    def rotate_log(self):
        """Rotate log files to save space."""
        try:
            # Check current log size
            if os.path.exists('bot.log'):
                size = os.path.getsize('bot.log')
                if size > self.max_file_size:
                    # Rotate logs
                    for i in range(self.max_files - 1, 0, -1):
                        old_file = f'bot.log.{i}'
                        new_file = f'bot.log.{i + 1}'
                        if os.path.exists(old_file):
                            if os.path.exists(new_file):
                                os.remove(new_file)
                            os.rename(old_file, new_file)
                    
                    # Move current log
                    if os.path.exists('bot.log.1'):
                        os.remove('bot.log.1')
                    os.rename('bot.log', 'bot.log.1')
                    
                    # Create new log
                    self._setup_logger()
                    self.logger.info("Log rotated due to size limit")
                    
        except Exception as e:
            print(f"Log rotation failed: {e}")

def check_system_requirements():
    """Check if system meets minimum requirements."""
    storage = shutil.disk_usage('.')
    storage_gb = storage.free / (1024**3)
    memory = psutil.virtual_memory()
    memory_gb = memory.available / (1024**3)
    
    print(f"System Check:")
    print(f"  Available Storage: {storage_gb:.1f} GB")
    print(f"  Available Memory: {memory_gb:.1f} GB")
    
    if storage_gb < 0.5:  # 500MB minimum
        print("  ⚠️  WARNING: Low storage space")
        
    if memory_gb < 0.5:  # 500MB minimum
        print("  ⚠️  WARNING: Low memory")
        
    return storage_gb >= 0.3 and memory_gb >= 0.3  # 300MB minimum

if __name__ == "__main__":
    # Test resource monitoring
    if not check_system_requirements():
        print("System does not meet minimum requirements")
        sys.exit(1)
        
    limits = ResourceLimits()
    monitor = ResourceMonitor(limits)
    
    status = monitor.check_resources()
    print(f"Resource Status: {status}")
    print(f"Runtime Stats: {monitor.get_runtime_stats()}")
