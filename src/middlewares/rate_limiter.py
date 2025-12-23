from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify
import os
from datetime import datetime
from src.utils import logger 

# Inicializar el limiter (esto lo usarás en tu app.py)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No aplicar límites por defecto
    storage_uri="memory://",  # Puedes usar Redis: "redis://localhost:6379"
)

def rate_limit_exceeded_handler(e):
    """Handler personalizado cuando se excede el rate limit"""
    logger.warning('Rate limit excedido', extra={
        'ip': get_remote_address(),
        'endpoint': e.description
    })
    
    return jsonify({
        'success': False,
        'message': 'Demasiadas peticiones, por favor intenta más tarde',
        'timestamp': datetime.utcnow().isoformat()
    }), 429

# Configuración del rate limiter general
def get_general_limit():
    """Rate limiter general para toda la API"""
    window_ms = int(os.getenv('RATE_LIMIT_WINDOW_MS', 15 * 60 * 1000))
    max_requests = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', 100))
    
    # Convertir milisegundos a formato de flask-limiter (por ejemplo: "100 per 15 minutes")
    window_minutes = window_ms // (60 * 1000)
    return f"{max_requests} per {window_minutes} minutes"

# Configuración del rate limiter para creación
CREATE_LIMIT = "20 per hour"  # 20 creaciones por hora