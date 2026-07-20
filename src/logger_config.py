"""Logging configuration for the deployer."""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.config import LoggingConfig


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class LoggerManager:
    """Manages application logging."""

    _instance: Optional['LoggerManager'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls, config: Optional[LoggingConfig] = None):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(config)
        return cls._instance

    def _initialize(self, config: Optional[LoggingConfig] = None) -> None:
        """Initialize logger."""
        self.config = config or LoggingConfig()
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup logger with handlers."""
        self._logger = logging.getLogger("deployer")
        self._logger.setLevel(getattr(logging, self.config.level))
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.level))
        
        if self.config.format == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler
        log_path = Path(self.config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(self.config.file_path)
        file_handler.setLevel(getattr(logging, self.config.level))
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Get logger instance."""
        return self._logger

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance."""
        cls._instance = None
        cls._logger = None


def get_logger(name: str = "deployer") -> logging.Logger:
    """Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    manager = LoggerManager()
    return logging.getLogger(name)
