from functools import wraps
from flask import request
from src.utils import error_response, verify_token, logger
from src.models.user import User

def authenticate(func):
    """
    Middleware para verificar JWT
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return error_response('Token de autenticación no proporcionado', 401)
            
            token = auth_header[7:]  # Remover "Bearer "
            
            # Verificar y decodificar token
            decoded = verify_token(token)
            
            # Opcional: Verificar que el usuario existe y está activo
            user = User.query.filter_by(id=decoded['id']).first()
            
            if not user:
                return error_response('Usuario no encontrado', 401)
            
            if not user.is_active:
                return error_response('Usuario inactivo', 403)
            
            # Agregar usuario al request
            request.user = {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
            
            logger.debug('Usuario autenticado', extra={
                'userId': user.id,
                'email': user.email,
                'role': user.role
            })
            
            return func(*args, **kwargs)
            
        except Exception as error:
            logger.warning('Error en autenticación', extra={
                'error': str(error),
                'ip': request.remote_addr,
                'url': request.url
            })
            
            error_message = str(error)
            if error_message == 'Token expirado':
                return error_response('Tu sesión ha expirado, por favor inicia sesión nuevamente', 401)
            
            if error_message == 'Token inválido':
                return error_response('Token de autenticación inválido', 401)
            
            return error_response('Error al verificar autenticación', 401)
    
    return wrapper


def authorize(*allowed_roles):
    """
    Middleware para verificar roles
    @param allowed_roles: Roles permitidos ['admin', 'user']
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'user'):
                return error_response('Usuario no autenticado', 401)
            
            if request.user['role'] not in allowed_roles:
                logger.warning('Acceso denegado por rol', extra={
                    'userId': request.user['id'],
                    'userRole': request.user['role'],
                    'requiredRoles': list(allowed_roles),
                    'url': request.url
                })
                
                return error_response(
                    'No tienes permisos para acceder a este recurso',
                    403
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def authorize_owner_or_admin(param_name='userId'):
    """
    Middleware para verificar que el usuario accede a sus propios recursos
    o es admin
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resource_user_id = kwargs.get(param_name) or request.get_json(silent=True, force=True).get(param_name)
            current_user_id = request.user['id']
            is_admin = request.user['role'] == 'admin'
            
            if str(resource_user_id) != str(current_user_id) and not is_admin:
                logger.warning('Acceso denegado - no es owner ni admin', extra={
                    'userId': current_user_id,
                    'resourceUserId': resource_user_id,
                    'url': request.url
                })
                
                return error_response(
                    'No tienes permisos para acceder a este recurso',
                    403
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def optional_auth(func):
    """
    Middleware opcional de autenticación
    Si hay token, lo valida. Si no hay, continúa sin user
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
                decoded = verify_token(token)
                
                user = User.query.filter_by(id=decoded['id']).first()
                
                if user and user.is_active:
                    request.user = {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role
                    }
        except:
            # Si falla, simplemente continuar sin usuario
            pass
        
        return func(*args, **kwargs)
    
    return wrapper