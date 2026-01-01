"""
CORS Middleware
Configuración de CORS para la API
"""
from flask_cors import CORS


def setup_cors(app):
    """
    Configura CORS
    Equivalente a configuración de CORS en Express
    """
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],  # En producción, especificar origins exactos
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
