"""
Constants - Application constants
Equivalente a src/constants/index.js
"""

# Roles de usuario
class UserRoles:
    USER = 'user'
    ADMIN = 'admin'
    
    @classmethod
    def all(cls):
        return [cls.USER, cls.ADMIN]


# Status codes HTTP
class HttpStatus:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500


# Mensajes de error comunes
class ErrorMessages:
    VALIDATION_ERROR = 'Error de validación'
    UNAUTHORIZED = 'No autorizado'
    FORBIDDEN = 'Acceso prohibido'
    NOT_FOUND = 'Recurso no encontrado'
    CONFLICT = 'Conflicto de recursos'
    INTERNAL_ERROR = 'Error interno del servidor'
    
    # Auth
    INVALID_CREDENTIALS = 'Credenciales inválidas'
    TOKEN_EXPIRED = 'Token expirado'
    TOKEN_INVALID = 'Token inválido'
    USER_NOT_FOUND = 'Usuario no encontrado'
    EMAIL_ALREADY_EXISTS = 'El email ya está registrado'
    
    # Login attempts
    ACCOUNT_BLOCKED = 'Cuenta bloqueada debido a múltiples intentos fallidos'


# Mensajes de éxito comunes
class SuccessMessages:
    CREATED = 'Recurso creado exitosamente'
    UPDATED = 'Recurso actualizado exitosamente'
    DELETED = 'Recurso eliminado exitosamente'
    
    # Auth
    REGISTER_SUCCESS = 'Usuario registrado exitosamente'
    LOGIN_SUCCESS = 'Login exitoso'
    LOGOUT_SUCCESS = 'Logout exitoso'
    TOKEN_REFRESHED = 'Token refrescado exitosamente'


# Configuración de paginación
class Pagination:
    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100


# Configuración de Login Attempts
class LoginAttempts:
    MAX_ATTEMPTS = 5
    BLOCK_DURATION_MINUTES = 15


# JWT Configuration
class JWTConfig:
    ACCESS_TOKEN_EXPIRY_MINUTES = 15
    REFRESH_TOKEN_EXPIRY_DAYS = 7


# Redis Keys Prefixes
class RedisKeys:
    TOKEN_BLACKLIST = 'token:blacklist:'
    REFRESH_TOKEN = 'token:refresh:'
    RATE_LIMIT = 'rate:limit:'
    IDEMPOTENCY = 'idempotency:'


__all__ = [
    'UserRoles',
    'HttpStatus',
    'ErrorMessages',
    'SuccessMessages',
    'Pagination',
    'LoginAttempts',
    'JWTConfig',
    'RedisKeys'
]
