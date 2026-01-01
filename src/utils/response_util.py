"""
Response Utility - API response formatter
Equivalente a src/utils/response.js
"""
from flask import jsonify
from typing import Any, Optional


class ApiResponse:
    """
    API Response formatter
    Equivalente a ApiResponse en Node.js
    """
    
    @staticmethod
    def success(
        message: str,
        data: Optional[Any] = None,
        status_code: int = 200
    ):
        """
        Respuesta exitosa
        Equivalente a ApiResponse.success() en Node.js
        """
        response = {
            'success': True,
            'message': message
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str,
        code: str = 'ERROR',
        details: Optional[Any] = None,
        status_code: int = 500
    ):
        """
        Respuesta de error
        Equivalente a ApiResponse.error() en Node.js
        """
        response = {
            'success': False,
            'message': message,
            'code': code
        }
        
        if details is not None:
            response['details'] = details
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(message: str, data: Optional[Any] = None):
        """201 Created"""
        return ApiResponse.success(message, data, 201)
    
    @staticmethod
    def no_content():
        """204 No Content"""
        return '', 204
    
    @staticmethod
    def bad_request(message: str = 'Bad request', details: Optional[Any] = None):
        """400 Bad Request"""
        return ApiResponse.error(message, 'BAD_REQUEST', details, 400)
    
    @staticmethod
    def unauthorized(message: str = 'Unauthorized', details: Optional[Any] = None):
        """401 Unauthorized"""
        return ApiResponse.error(message, 'UNAUTHORIZED', details, 401)
    
    @staticmethod
    def forbidden(message: str = 'Forbidden', details: Optional[Any] = None):
        """403 Forbidden"""
        return ApiResponse.error(message, 'FORBIDDEN', details, 403)
    
    @staticmethod
    def not_found(message: str = 'Not found', details: Optional[Any] = None):
        """404 Not Found"""
        return ApiResponse.error(message, 'NOT_FOUND', details, 404)
    
    @staticmethod
    def conflict(message: str = 'Conflict', details: Optional[Any] = None):
        """409 Conflict"""
        return ApiResponse.error(message, 'CONFLICT', details, 409)
    
    @staticmethod
    def validation_error(message: str = 'Validation error', errors: Optional[Any] = None):
        """422 Unprocessable Entity - Validation Error"""
        return ApiResponse.error(message, 'VALIDATION_ERROR', errors, 422)
    
    @staticmethod
    def internal_error(message: str = 'Internal server error'):
        """500 Internal Server Error"""
        return ApiResponse.error(message, 'INTERNAL_ERROR', None, 500)
