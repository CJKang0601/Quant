"""Logging configuration for AI Investment Agent."""
import logging
from config.settings import LOG_LEVEL, LOG_FORMAT

# Create logger
def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, LOG_LEVEL))
        formatter = logging.Formatter(LOG_FORMAT)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger
