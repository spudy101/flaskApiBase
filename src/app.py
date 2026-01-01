"""
Flask Application Factory
Equivalente a src/app.js en Node.js
"""
from flask import Flask
from config.database import db, init_db
from config.settings import config
from src.middlewares.cors_middleware import setup_cors
from src.middlewares.error_middleware import register_error_handlers
from src.routes import register_blueprints
from src.utils.logger_util import logger
import os


def create_app(env=None):
    """
    Application factory
    Crea y configura la aplicación Flask
    
    Args:
        env: Environment (development, test, production)
    
    Returns:
        Flask app instance
    """
    # Crear app
    app = Flask(__name__)
    
    # Determinar environment
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    # Cargar configuración
    app.config.from_object(config[env])
    
    logger.info(f'🚀 Starting Flask API in {env} mode')
    
    # Inicializar base de datos
    init_db(app)
    
    # Setup CORS
    setup_cors(app)
    
    # Registrar blueprints (routes)
    register_blueprints(app)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log cada request"""
        from flask import request
        logger.info(
            f'{request.method} {request.path}',
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    
    @app.after_request
    def log_response(response):
        """Log cada response"""
        from flask import request
        logger.info(
            f'{request.method} {request.path} - {response.status_code}',
            status_code=response.status_code
        )
        return response
    
    logger.info('✅ Flask app configured successfully')
    
    return app
