"""
Logger Utility - Logging configuration
Equivalente a src/utils/logger.js
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


class LoggerUtil:
    """Logger utility class"""
    
    @staticmethod
    def setup_logger(name: str = 'flask_api') -> logging.Logger:
        """
        Configura y retorna logger
        Equivalente a winston logger en Node.js
        """
        logger = logging.getLogger(name)
        
        # Evitar duplicados
        if logger.handlers:
            return logger
        
        # Nivel de log desde environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Formato JSON
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (rotating)
        log_file = os.getenv('LOG_FILE', 'logs/app.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger


# Singleton logger instance
logger = LoggerUtil.setup_logger()


def log_info(message: str, **kwargs):
    """Helper para log info"""
    logger.info(message, extra=kwargs)


def log_error(message: str, **kwargs):
    """Helper para log error"""
    logger.error(message, extra=kwargs, exc_info=True)


def log_warning(message: str, **kwargs):
    """Helper para log warning"""
    logger.warning(message, extra=kwargs)


def log_debug(message: str, **kwargs):
    """Helper para log debug"""
    logger.debug(message, extra=kwargs)
