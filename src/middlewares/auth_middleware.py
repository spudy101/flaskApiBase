"""
Auth Middleware - Authentication and Authorization
Equivalente a src/middlewares/auth.middleware.js
"""
from functools import wraps
from flask import request, g
import jwt as pyjwt
from src.utils.jwt_util import jwt_util
from src.utils.response_util import ApiResponse
from src.repositories.user_repository import user_repository


def authenticate():
    """
    Middleware de autenticación
    Equivalente a authenticate() en Node.js
    
    Verifica el token JWT y agrega el usuario a g.user
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obtener token del header Authorization
                auth_header = request.headers.get('Authorization', '')
                
                if not auth_header or not auth_header.startswith('Bearer '):
                    return ApiResponse.unauthorized('Token no proporcionado')
                
                # Extraer token
                token = auth_header.replace('Bearer ', '')
                
                # Verificar token
                try:
                    payload = jwt_util.verify_access_token(token)
                except pyjwt.ExpiredSignatureError:
                    return ApiResponse.unauthorized('Token expirado')
                except pyjwt.InvalidTokenError:
                    return ApiResponse.unauthorized('Token inválido')
                
                # Verificar que el usuario existe y está activo
                user = user_repository.find_by_id(payload['id'])
                
                if not user or not user.is_active:
                    return ApiResponse.unauthorized('Usuario no encontrado o inactivo')
                
                # Agregar usuario a g (Flask's application context)
                g.user = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role.value if hasattr(user.role, 'value') else user.role
                }
                g.token = token
                
                # Continuar con la request
                return f(*args, **kwargs)
                
            except Exception as e:
                return ApiResponse.internal_error(f'Error en autenticación: {str(e)}')
        
        return decorated_function
    return decorator


def authorize(allowed_roles: list):
    """
    Middleware de autorización
    Equivalente a authorize() en Node.js
    
    Verifica que el usuario tenga uno de los roles permitidos
    Debe usarse DESPUÉS de authenticate()
    
    Usage:
        @authenticate()
        @authorize(['admin'])
        def some_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # El usuario ya fue agregado por authenticate()
                user = g.get('user')
                
                if not user:
                    return ApiResponse.unauthorized('No autenticado')
                
                # Verificar rol
                user_role = user.get('role')
                
                if user_role not in allowed_roles:
                    return ApiResponse.forbidden(
                        f'Requiere uno de los siguientes roles: {", ".join(allowed_roles)}'
                    )
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return ApiResponse.internal_error(f'Error en autorización: {str(e)}')
        
        return decorated_function
    return decorator


def optional_auth():
    """
    Middleware de autenticación opcional
    Agrega el usuario a g.user si el token es válido,
    pero NO retorna error si no hay token
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization', '')
                
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.replace('Bearer ', '')
                    
                    try:
                        payload = jwt_util.verify_access_token(token)
                        user = user_repository.find_by_id(payload['id'])
                        
                        if user and user.is_active:
                            g.user = {
                                'id': user.id,
                                'email': user.email,
                                'name': user.name,
                                'role': user.role.value if hasattr(user.role, 'value') else user.role
                            }
                    except:
                        pass  # Ignorar errores, es autenticación opcional
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return ApiResponse.internal_error(f'Error: {str(e)}')
        
        return decorated_function
    return decorator
