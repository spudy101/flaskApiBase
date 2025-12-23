# utils/logger.py
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from datetime import datetime

# ------------------------
# Niveles personalizados
# ------------------------
LEVELS = {
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'http': 15,
    'debug': logging.DEBUG
}

def http(self, message, *args, **kwargs):
    if self.isEnabledFor(15):
        self._log(15, message, args, **kwargs)

logging.Logger.http = http

logging.addLevelName(15, 'HTTP')

# ------------------------
# Colores
# ------------------------
COLORS = {
    'ERROR': '\033[91m',
    'WARNING': '\033[93m',
    'INFO': '\033[92m',
    'HTTP': '\033[95m',
    'DEBUG': '\033[94m',
    'RESET': '\033[0m'
}

# ------------------------
# Formatters
# ------------------------
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelname, COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{COLORS['RESET']}"
        record.msg = f"{color}{record.getMessage()}{COLORS['RESET']}"
        return super().format(record)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_data['stack'] = self.formatException(record.exc_info)
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        return json.dumps(log_data, ensure_ascii=False)

# ------------------------
# Helpers
# ------------------------
def get_level():
    env = os.getenv('NODE_ENV', 'development')
    return logging.DEBUG if env == 'development' else logging.WARNING

# ------------------------
# Setup logger
# ------------------------
def setup_logger():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger('app')
    logger.setLevel(get_level())
    logger.propagate = False

    # ⚠️ IMPORTANTE: evitar handlers duplicados
    if logger.handlers:
        return logger

    env = os.getenv('NODE_ENV', 'development')

    formatter = (
        JsonFormatter()
        if env == 'production'
        else ColoredFormatter(
            '%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )

    # ------------------------
    # Consola (UTF-8)
    # ------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.stream.reconfigure(encoding='utf-8')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ------------------------
    # Error log (UTF-8)
    # ------------------------
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=5_242_880,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JsonFormatter() if env == 'production' else formatter)
    logger.addHandler(error_handler)

    # ------------------------
    # Combined log (UTF-8)
    # ------------------------
    combined_handler = RotatingFileHandler(
        'logs/combined.log',
        maxBytes=5_242_880,
        backupCount=5,
        encoding='utf-8'
    )
    combined_handler.setFormatter(JsonFormatter() if env == 'production' else formatter)
    logger.addHandler(combined_handler)

    return logger

logger = setup_logger()
