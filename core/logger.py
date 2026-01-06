#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Logging System
Production-ready logging with file rotation and structured output
"""

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LogLevel(Enum):
    """Log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class StructuredLogger:
    """
    Structured logger with file rotation and console output
    Thread-safe logging implementation
    """
    
    def __init__(
        self,
        name: str = "WindowsOptimizer",
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[Path] = None,
        console: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level.value)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level.value)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal log method with context"""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {context}"
        self.logger.log(level, message)
    
    def exception(self, message: str, exc_info: Optional[Exception] = None) -> None:
        """Log exception with traceback"""
        self.logger.exception(message, exc_info=exc_info)


# Global logger instance
_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "WindowsOptimizer", **kwargs) -> StructuredLogger:
    """Get or create logger instance"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name, **kwargs)
    return _logger


# Alias for convenience
Logger = StructuredLogger

