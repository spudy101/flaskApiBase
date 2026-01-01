"""
Middlewares package
"""
from .auth_middleware import authenticate, authorize, optional_auth
from .error_middleware import register_error_handlers
from .cors_middleware import setup_cors

__all__ = [
    'authenticate',
    'authorize',
    'optional_auth',
    'register_error_handlers',
    'setup_cors'
]
