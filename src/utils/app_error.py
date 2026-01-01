"""
AppError - Custom error class
Equivalente a src/utils/AppError.js
"""
from typing import Optional, Dict, Any


class AppError(Exception):
    """
    Custom application error
    Equivalente a AppError en Node.js
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = 'INTERNAL_ERROR',
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
    
    def to_dict(self) -> dict:
        """Convierte el error a diccionario para JSON response"""
        error_dict = {
            'success': False,
            'message': self.message,
            'code': self.code
        }
        
        if self.details:
            error_dict['details'] = self.details
        
        return error_dict
    
    # ========================================
    # Static factory methods para errores comunes
    # ========================================
    
    @staticmethod
    def bad_request(message: str = 'Bad request', details: Any = None) -> 'AppError':
        """400 Bad Request"""
        return AppError(message, 400, 'BAD_REQUEST', details)
    
    @staticmethod
    def unauthorized(message: str = 'Unauthorized', details: Any = None) -> 'AppError':
        """401 Unauthorized"""
        return AppError(message, 401, 'UNAUTHORIZED', details)
    
    @staticmethod
    def forbidden(message: str = 'Forbidden', details: Any = None) -> 'AppError':
        """403 Forbidden"""
        return AppError(message, 403, 'FORBIDDEN', details)
    
    @staticmethod
    def not_found(message: str = 'Not found', details: Any = None) -> 'AppError':
        """404 Not Found"""
        return AppError(message, 404, 'NOT_FOUND', details)
    
    @staticmethod
    def conflict(message: str = 'Conflict', details: Any = None) -> 'AppError':
        """409 Conflict"""
        return AppError(message, 409, 'CONFLICT_ERROR', details)
    
    @staticmethod
    def unprocessable(message: str = 'Unprocessable entity', details: Any = None) -> 'AppError':
        """422 Unprocessable Entity"""
        return AppError(message, 422, 'VALIDATION_ERROR', details)
    
    @staticmethod
    def too_many_requests(message: str = 'Too many requests', details: Any = None) -> 'AppError':
        """429 Too Many Requests"""
        return AppError(message, 429, 'TOO_MANY_REQUESTS', details)
    
    @staticmethod
    def internal(message: str = 'Internal server error', details: Any = None) -> 'AppError':
        """500 Internal Server Error"""
        return AppError(message, 500, 'INTERNAL_ERROR', details)
    
    def __str__(self):
        return f'{self.code}: {self.message}'
    
    def __repr__(self):
        return f'AppError({self.status_code}, {self.code}, {self.message})'
