import os
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def setup_rate_limiting(app: Flask):
    """
    Configura rate limiting para la aplicación
    Equivalente al rate limiter de Express
    """
    
    if os.getenv('RATE_LIMIT_ENABLED', 'True').lower() != 'true':
        return
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{os.getenv('RATE_LIMIT_PER_MINUTE', 60)}/minute"],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'success': False,
            'message': 'Demasiadas solicitudes, espera un momento'
        }), 429
    
    return limiter

__all__ = ['setup_rate_limiting']
