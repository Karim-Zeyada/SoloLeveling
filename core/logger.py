"""
Logging configuration for Solo Leveling game.
Replaces print statements with proper logging for better debugging and monitoring.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Log format constants
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
DETAILED_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"


class GameLogger:
    """
    Centralized logging configuration for the game.
    
    Usage:
        from core.logger import get_logger
        logger = get_logger('game_engine')
        logger.info('Game started')
        logger.debug('Player position: %s, %s', x, y)
    """
    
    _instance: Optional['GameLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'GameLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._loggers: dict[str, logging.Logger] = {}
        self._root_logger = logging.getLogger('solo_leveling')
        self._root_logger.setLevel(logging.DEBUG)
        
        # Console handler (INFO level by default)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        self._root_logger.addHandler(console_handler)
        
        self._initialized = True
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module."""
        if name not in self._loggers:
            logger = self._root_logger.getChild(name)
            self._loggers[name] = logger
        return self._loggers[name]
    
    def set_level(self, level: int) -> None:
        """Set the logging level for all loggers."""
        self._root_logger.setLevel(level)
        for handler in self._root_logger.handlers:
            handler.setLevel(level)
    
    def enable_debug(self) -> None:
        """Enable debug logging to console."""
        self.set_level(logging.DEBUG)
        for handler in self._root_logger.handlers:
            handler.setFormatter(logging.Formatter(DETAILED_FORMAT, LOG_DATE_FORMAT))
    
    def add_file_handler(self, log_dir: str = "logs") -> None:
        """Add a file handler for persistent logging."""
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"game_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT, LOG_DATE_FORMAT))
        self._root_logger.addHandler(file_handler)


# Singleton accessor
_game_logger: Optional[GameLogger] = None


def get_logger(name: str = 'game') -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Module name for the logger (e.g., 'game_engine', 'entities', 'ui')
        
    Returns:
        Configured logger instance
    """
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    return _game_logger.get_logger(name)


def enable_debug_logging() -> None:
    """Enable debug-level logging with detailed format."""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    _game_logger.enable_debug()


def enable_file_logging(log_dir: str = "logs") -> None:
    """Enable file logging in addition to console."""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    _game_logger.add_file_handler(log_dir)
