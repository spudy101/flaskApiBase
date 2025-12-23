"""
Centralización de rutas
Equivalente a index.js de routes en Node.js
"""

from flask import Blueprint, jsonify
from datetime import datetime
import time
import os

# Importar blueprints de rutas específicas
from .auth_routes import auth_bp

# Crear blueprint principal (equivalente al router de Express)
main_bp = Blueprint('main', __name__)


# Health check endpoint
@main_bp.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    # Tiempo de inicio de la aplicación (simulando process.uptime())
    # En producción, esto debería guardarse cuando inicia la app
    return jsonify({
        'success': True,
        'message': 'API funcionando correctamente',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'environment': os.getenv('FLASK_ENV', 'development')
    }), 200


# Función para registrar todos los blueprints en la app
def register_routes(app):
    """
    Registra todos los blueprints en la aplicación
    
    Args:
        app: Instancia de Flask
    """
    API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
    
    # Registrar blueprint principal (health check)
    app.register_blueprint(main_bp, url_prefix=API_PREFIX)
    
    # Registrar blueprints de rutas específicas
    app.register_blueprint(auth_bp, url_prefix=f'{API_PREFIX}/auth')


# Exportar blueprints para uso individual si es necesario
__all__ = [
    'main_bp',
    'auth_bp',
    'user_bp',
    'product_bp',
    'register_routes'
]