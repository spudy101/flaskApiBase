import hashlib
import json
import time
from datetime import datetime
from flask import request
from src.utils import error_response, logger
from functools import wraps

# Almacén en memoria para requests en proceso
# En producción, usar Redis
request_store = {}

def cleanup_old_requests():
    """Limpiar requests antiguos"""
    now = time.time()
    keys_to_delete = []
    
    for key, value in request_store.items():
        if now - value['timestamp'] > 5 * 60:  # 5 minutos
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del request_store[key]

def generate_request_key(req):
    """Genera una clave única para la request"""
    user_id = getattr(req, 'user', {}).get('id', 'anonymous') if hasattr(req, 'user') else 'anonymous'
    method = req.method
    path = req.path
    body = json.dumps(req.get_json(silent=True) or {})
    
    data = f"{user_id}-{method}-{path}-{body}"
    return hashlib.md5(data.encode()).hexdigest()

def request_lock(timeout=5000, message='Petición duplicada en proceso, por favor espera'):
    """
    Middleware para prevenir requests duplicados simultáneos
    Útil para prevenir doble submit en formularios
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Solo aplicar a métodos que modifican datos
            if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return func(*args, **kwargs)
            
            # Limpiar requests antiguos
            cleanup_old_requests()
            
            request_key = generate_request_key(request)
            
            # Verificar si existe una request idéntica en proceso
            if request_key in request_store:
                existing_request = request_store[request_key]
                time_diff = (time.time() - existing_request['timestamp']) * 1000  # Convertir a ms
                
                # Si la request lleva menos del timeout, rechazar
                if time_diff < timeout:
                    logger.warning('Request duplicado detectado', extra={
                        'requestKey': request_key,
                        'userId': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None,
                        'method': request.method,
                        'path': request.path,
                        'timeDiff': f'{int(time_diff)}ms'
                    })
                    
                    return error_response(message, 409)
                
                # Si ya pasó el timeout, eliminar y permitir
                del request_store[request_key]
            
            # Registrar la nueva request
            request_store[request_key] = {
                'timestamp': time.time(),
                'userId': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None,
                'method': request.method,
                'path': request.path
            }
            
            logger.debug('Request registrado en lock', extra={
                'requestKey': request_key,
                'userId': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None,
                'method': request.method,
                'path': request.path
            })
            
            try:
                # Ejecutar la función
                result = func(*args, **kwargs)
                return result
            finally:
                # Cleanup después de que termine la request
                if request_key in request_store:
                    del request_store[request_key]
                    logger.debug('Request lock liberado', extra={'requestKey': request_key})
        
        return wrapper
    return decorator

def get_request_lock_stats():
    """Obtener estadísticas del request lock"""
    now = time.time()
    return {
        'activeRequests': len(request_store),
        'requests': [
            {
                'key': key,
                'age': int((now - value['timestamp']) * 1000),
                **value
            }
            for key, value in request_store.items()
        ]
    }

def clear_request_store():
    """Limpiar el request store (solo para testing)"""
    request_store.clear()