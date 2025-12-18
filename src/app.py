import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

def create_app():
    """Factory para crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # ===================================
    # CONFIGURACIÓN BÁSICA
    # ===================================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Ajustar según necesidades
    app.config['JWT_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    
    # Límites de tamaño de request
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    
    # ===================================
    # CONFIGURACIÓN DE CORS
    # ===================================
    if os.getenv('FLASK_ENV') == 'development':
        CORS(app, 
             origins='*',
             methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
             allow_headers=['Content-Type', 'Authorization', 'timestamp'],
             supports_credentials=True)
    else:
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
        CORS(app,
             origins=allowed_origins,
             methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
             allow_headers=['Content-Type', 'Authorization', 'timestamp'],
             supports_credentials=True)
    
    # ===================================
    # INICIALIZAR JWT
    # ===================================
    jwt = JWTManager(app)
    
    # Manejador de errores JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'success': False,
            'message': 'Token inválido',
            'code': 'INVALID_TOKEN'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token expirado',
            'code': 'TOKEN_EXPIRED'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token no proporcionado',
            'code': 'AUTH_REQUIRED'
        }), 401
    
    # ===================================
    # CONFIGURAR RATE LIMITING
    # ===================================
    from src.middlewares.rate_limit import setup_rate_limiting
    setup_rate_limiting(app)
    
    # ===================================
    # LOGGING
    # ===================================
    from src.config.logging_config import setup_logging
    setup_logging(app)
    
    # ===================================
    # BEFORE REQUEST - Logging
    # ===================================
    @app.before_request
    def log_request():
        if os.getenv('FLASK_ENV') == 'development':
            app.logger.info(f"{request.method} {request.path}")
    
    # ===================================
    # RUTAS PRINCIPALES
    # ===================================
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        import time
        return jsonify({
            'status': 'OK',
            'timestamp': time.time(),
            'environment': os.getenv('FLASK_ENV', 'production'),
        }), 200
    
    # Registrar blueprints (rutas)
    from src.routes import register_routes
    register_routes(app)
    
    # Configurar Swagger (solo en desarrollo)
    if os.getenv('FLASK_ENV') == 'development':
        from src.config.swagger import setup_swagger
        setup_swagger(app)
    
    # ===================================
    # MANEJO DE ERRORES
    # ===================================
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': f'Ruta no encontrada: {request.method} {request.path}'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': f'Método no permitido: {request.method}'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Error 500: {str(error)}')
        if os.getenv('FLASK_ENV') == 'development':
            return jsonify({
                'success': False,
                'message': str(error)
            }), 500
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        if os.getenv('FLASK_ENV') == 'development':
            return jsonify({
                'success': False,
                'message': str(error),
                'type': type(error).__name__
            }), 500
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500
    
    return app
