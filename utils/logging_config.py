"""
Logging configuration for CatGen
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(log_level: str = "INFO",
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_dir: Path = Path("logs"),
                 max_bytes: int = 10 * 1024 * 1024,  # 10 MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Configure application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Root logger for the application
    """
    # Create log directory
    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger for CatGen
    logger = logging.getLogger('catgen')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler (rotating)
    if log_to_file:
        log_file = log_dir / f"catgen_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # Create separate error log file
    if log_to_file:
        error_log_file = log_dir / f"catgen_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    logger.info(f"Logging initialized: level={log_level}, file={log_to_file}, console={log_to_console}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        name: Module name (e.g., 'catgen.breeding')
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogCapture:
    """Context manager for capturing log messages"""
    
    def __init__(self, logger_name: str = 'catgen', level: int = logging.INFO):
        self.logger = logging.getLogger(logger_name)
        self.level = level
        self.handler = None
        self.messages = []
    
    def __enter__(self):
        """Start capturing logs"""
        self.handler = logging.handlers.MemoryHandler(capacity=1000)
        self.handler.setLevel(self.level)
        self.logger.addHandler(self.handler)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing logs"""
        if self.handler:
            self.handler.flush()
            self.logger.removeHandler(self.handler)
            self.messages = [record.getMessage() for record in self.handler.buffer]
    
    def get_messages(self) -> list:
        """Get captured log messages"""
        return self.messages


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
            raise
    return wrapper


def log_performance(func):
    """Decorator to log function performance"""
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    
    return wrapper