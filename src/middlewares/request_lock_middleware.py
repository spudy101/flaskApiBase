from functools import wraps
from flask import request, jsonify
from typing import Callable, Optional
from src.utils.request_lock import create_request_lock

# Cache de locks por ruta
route_locks = {}

def with_request_lock(key_extractor: Callable[[any], Optional[str]]):
    """
    Decorator para aplicar request locking
    Equivalente a withRequestLock() de Node.js
    
    Args:
        key_extractor: Función que extrae la key del request
                      Ejemplo: lambda: request.usuario.get('party_uuid') if hasattr(request, 'usuario') else None
    
    Usage:
        @app.route('/api/perfil')
        @verificar_autenticacion
        @with_request_lock(lambda: request.usuario.get('id_usuario'))
        def get_perfil():
            return jsonify(data='...')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            route_key = request.path
            
            # Crear lock para esta ruta si no existe
            if route_key not in route_locks:
                print(f"Creando request lock para ruta: {route_key}")
                route_locks[route_key] = create_request_lock()
            
            lock = route_locks[route_key]
            
            # Extraer la key del request
            try:
                lock_key = key_extractor()
            except Exception as e:
                print(f"Error extrayendo lock key: {str(e)}")
                lock_key = None
            
            if not lock_key:
                return jsonify({
                    'estado_solicitud': 0,
                    'message': 'No se pudo identificar la solicitud'
                }), 400
            
            # Intentar adquirir el lock
            if not lock.acquire(lock_key):
                return jsonify({
                    'estado_solicitud': 0,
                    'message': 'Ya hay una solicitud en proceso.'
                }), 429
            
            # Flag para evitar doble release
            released = [False]
            
            def release_lock():
                if not released[0]:
                    released[0] = True
                    lock.release(lock_key)
            
            try:
                # Ejecutar la función
                response = f(*args, **kwargs)
                return response
            finally:
                # Siempre liberar el lock
                release_lock()
        
        return decorated_function
    return decorator

__all__ = ['with_request_lock']
