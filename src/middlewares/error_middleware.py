"""
Error Middleware - Global error handlers
Equivalente a src/middlewares/error.middleware.js
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from src.utils.app_error import AppError
from src.utils.logger_util import logger


def register_error_handlers(app):
    """
    Registra manejadores de errores globales
    Equivalente a error middleware en Express
    """
    
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        """Maneja errores de aplicación personalizados"""
        logger.error(
            f'AppError: {error.message}',
            status_code=error.status_code,
            code=error.code,
            details=error.details
        )
        
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Maneja excepciones HTTP de Werkzeug"""
        logger.warning(
            f'HTTPException: {error.description}',
            status_code=error.code
        )
        
        response = {
            'success': False,
            'message': error.description or 'HTTP Error',
            'code': f'HTTP_{error.code}'
        }
        
        return jsonify(response), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Maneja 404 Not Found"""
        response = {
            'success': False,
            'message': 'Endpoint no encontrado',
            'code': 'NOT_FOUND'
        }
        
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Maneja 405 Method Not Allowed"""
        response = {
            'success': False,
            'message': 'Método HTTP no permitido',
            'code': 'METHOD_NOT_ALLOWED'
        }
        
        return jsonify(response), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Maneja 500 Internal Server Error"""
        logger.error('Internal Server Error', error=str(error), exc_info=True)
        
        response = {
            'success': False,
            'message': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR'
        }
        
        return jsonify(response), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Maneja cualquier excepción no capturada"""
        logger.error(
            'Unexpected Error',
            error=str(error),
            error_type=type(error).__name__,
            exc_info=True
        )
        
        response = {
            'success': False,
            'message': 'Error inesperado',
            'code': 'UNEXPECTED_ERROR'
        }
        
        # En desarrollo, incluir detalles del error
        if app.config.get('DEBUG'):
            response['details'] = str(error)
        
        return jsonify(response), 500
