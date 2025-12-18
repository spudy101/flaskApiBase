import os
import logging
from flask import Flask

def setup_logging(app: Flask):
    """
    Configura el sistema de logging de la aplicación
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configurar nivel de log
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Formato de logs
    if os.getenv('FLASK_ENV') == 'development':
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    app.logger.addHandler(console_handler)
    
    return app.logger

__all__ = ['setup_logging']
