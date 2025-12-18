import os
import time
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import jwt

from src.utils.crypto_utils import desencriptar_mensaje
from src.utils.datos_utils import obtener_datos_usuario_por_token

SECRET_JWT_KEY = os.getenv('SECRET_JWT_KEY')

def verificar_autenticacion(f):
    """
    Decorator para verificar autenticación de usuario
    Equivalente a verificarAutenticacion middleware de Node.js
    
    Usage:
        @app.route('/protected')
        @verificar_autenticacion
        def protected_route():
            # req.usuario estará disponible
            return jsonify(usuario=request.usuario)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener el token de las cookies
            jwt_token = request.cookies.get('jwtToken')
            
            if not jwt_token:
                return jsonify({
                    'success': False,
                    'message': 'No autorizado. Token no proporcionado',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            # Verificar y decodificar el JWT
            try:
                info_jwt = jwt.decode(jwt_token, SECRET_JWT_KEY, algorithms=['HS256'])
                token = info_jwt.get('token')
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'success': False,
                    'message': 'Token expirado',
                    'code': 'TOKEN_EXPIRED'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'success': False,
                    'message': 'Token inválido',
                    'code': 'INVALID_TOKEN'
                }), 401
            
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'No autorizado. Token no proporcionado',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            # Obtener datos del usuario por token
            result = obtener_datos_usuario_por_token(token)
            
            if not result.get('success') or not result.get('data'):
                return jsonify({
                    'success': False,
                    'message': 'No autorizado. Sesión inválida o expirada',
                    'code': 'INVALID_SESSION'
                }), 401
            
            # Agregar usuario al contexto de request
            request.usuario = result['data']
            
            return f(*args, **kwargs)
            
        except Exception as error:
            print(f'Error en middleware de autenticación: {str(error)}')
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(error)
            }), 500
    
    return decorated_function

def verificar_timestamp(f):
    """
    Decorator para verificar timestamp encriptado
    Equivalente a verificarTimestamp middleware de Node.js
    
    Usage:
        @app.route('/protected')
        @verificar_timestamp
        def protected_route():
            # El timestamp fue validado
            return jsonify(status='ok')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener el timestamp del header
            timestamp = request.headers.get('timestamp')
            
            if not timestamp:
                return jsonify({
                    'success': False,
                    'message': 'No autorizado. timestamp no proporcionado',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            # Desencriptar el timestamp
            try:
                timestamp_decrypt = desencriptar_mensaje(timestamp)
            except Exception:
                return jsonify({
                    'success': False,
                    'message': 'Timestamp inválido o corrupto',
                    'code': 'INVALID_TIMESTAMP'
                }), 401
            
            if not timestamp_decrypt:
                return jsonify({
                    'success': False,
                    'message': 'Timestamp inválido o corrupto',
                    'code': 'INVALID_TIMESTAMP'
                }), 401
            
            # Convertir el timestamp desencriptado a número
            try:
                timestamp_value = int(timestamp_decrypt)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de timestamp inválido',
                    'code': 'INVALID_TIMESTAMP_FORMAT'
                }), 401
            
            # Obtener el timestamp actual en milisegundos
            ahora = int(time.time() * 1000)
            
            # Calcular la diferencia en milisegundos
            diferencia = abs(ahora - timestamp_value)
            
            # Verificar que no haya pasado más de 1 minuto (60000 ms)
            UN_MINUTO_MS = 60000
            
            if diferencia > UN_MINUTO_MS:
                return jsonify({
                    'success': False,
                    'message': 'Timestamp expirado. La solicitud debe realizarse dentro de 1 minuto',
                    'code': 'TIMESTAMP_EXPIRED'
                }), 401
            
            # Guardar el timestamp en request para uso posterior
            request.timestamp_validado = timestamp_value
            
            return f(*args, **kwargs)
            
        except Exception as error:
            print(f'Error en middleware de verificación de timestamp: {str(error)}')
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor',
                'error': str(error)
            }), 500
    
    return decorated_function

__all__ = ['verificar_autenticacion', 'verificar_timestamp']
