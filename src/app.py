"""
Aplicación Flask principal
Equivalente a app.js de Node.js
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

from config.database import db
from src.utils.logger import logger
from src.routes import register_routes
from src.middlewares import error_handler, not_found_handler
from src.middlewares import limiter, rate_limit_exceeded_handler
from config.swagger import setup_swagger


def create_app(env='development'):
    """
    Factory para crear la aplicación Flask
    
    Args:
        env: Ambiente de ejecución (development, production)
        
    Returns:
        Instancia de Flask configurada
    """
    app = Flask(__name__)
    
    # ==================== CONFIGURACIÓN ====================
    app.config['ENV'] = env
    app.config['DEBUG'] = env == 'development'
    
    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = env == 'development'
    
    # ==================== SECURITY ====================
    # CORS - Configuración de orígenes permitidos
    cors_options = {
        'origins': os.getenv('CORS_ORIGIN', '*'),
        'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        'allow_headers': ['Content-Type', 'Authorization'],
        'supports_credentials': True,
        'max_age': 86400  # 24 horas
    }
    CORS(app, resources={r"/*": cors_options})
    
    # Security Headers (equivalente a Helmet)
    @app.after_request
    def set_security_headers(response):
        """Agregar headers de seguridad"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    # ==================== MIDDLEWARE ====================
    # Limitar tamaño de request body
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    
    # Trust proxy (para obtener IP real detrás de proxy/load balancer)
    app.config['PREFERRED_URL_SCHEME'] = 'https' if env == 'production' else 'http'
    
    # Request logger (equivalente a Morgan)
    @app.before_request
    def log_request():
        """Log de requests HTTP"""
        if env == 'development':
            logger.debug(f'{request.method} {request.path}')
        else:
            logger.http(f'{request.remote_addr} - "{request.method} {request.path}" - {request.user_agent}')
    
    # ==================== INICIALIZAR EXTENSIONES ====================
    # Database
    db.init_app(app)
    
    # Rate Limiter
    limiter.init_app(app)
    app.register_error_handler(429, rate_limit_exceeded_handler)
    
    # ==================== ROUTES ====================
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        api_prefix = os.getenv('API_PREFIX', '/api/v1')
        return jsonify({
            'success': True,
            'message': 'Bienvenido a la API',
            'version': '1.0.0',
            'documentation': f'{request.scheme}://{request.host}{api_prefix}/docs',
            'endpoints': {
                'health': f'{api_prefix}/health',
                'auth': f'{api_prefix}/auth',
                'users': f'{api_prefix}/users',
                'products': f'{api_prefix}/products'
            }
        })
    
    # Registrar todas las rutas
    register_routes(app)
    
    # ==================== SWAGGER DOCUMENTATION ====================
    setup_swagger(app)
    
    # ==================== ERROR HANDLING ====================
    # 404 - Not Found
    @app.errorhandler(404)
    def handle_404(error):
        return not_found_handler(error)
    
    # Error handler global
    @app.errorhandler(Exception)
    def handle_error(error):
        return error_handler(error)
    
    return app