"""
Configuración de Swagger/OpenAPI
"""

from flask_swagger_ui import get_swaggerui_blueprint
from flask import jsonify
import os
from .swagger_schemas.init import get_all_schemas
from .swagger_paths.init import get_all_paths


def setup_swagger(app):
    """
    Configurar Swagger UI y documentación OpenAPI
    
    Args:
        app: Instancia de Flask
    """
    API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
    PORT = os.getenv('PORT', '5000')
    
    # Especificación OpenAPI
    swagger_spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'API Flask + SQLAlchemy + PostgreSQL',
            'version': '1.0.0',
            'description': 'API RESTful con autenticación JWT, CRUD completo y buenas prácticas',
            'contact': {
                'name': 'Tu Nombre',
                'email': 'tu@email.com'
            },
            'license': {
                'name': 'MIT',
                'url': 'https://opensource.org/licenses/MIT'
            }
        },
        'servers': [
            {
                'url': f'http://localhost:{PORT}{API_PREFIX}',
                'description': 'Servidor de desarrollo'
            },
            {
                'url': f'https://tu-dominio.com{API_PREFIX}',
                'description': 'Servidor de producción'
            }
        ],
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'Ingresa tu token JWT en el formato: Bearer {token}'
                }
            },
            'schemas': get_all_schemas()  # ✨ Todos los schemas modularizados
        },
        'paths': get_all_paths(),  # ✨ Todos los paths modularizados
        'tags': [
            {'name': 'Auth', 'description': 'Endpoints de autenticación y gestión de perfil'},
            {'name': 'Users', 'description': 'Gestión de usuarios (Solo Admin)'},
            {'name': 'Products', 'description': 'Gestión de productos (CRUD completo)'},
            {'name': 'Orders', 'description': 'Gestión de órdenes'},
            {'name': 'Payments', 'description': 'Gestión de pagos'}
        ]
    }
    
    # Endpoint para servir el JSON spec
    @app.route(f'{API_PREFIX}/docs.json', methods=['GET'])
    def swagger_json():
        return jsonify(swagger_spec)
    
    # Configurar Swagger UI
    SWAGGER_URL = f'{API_PREFIX}/docs'
    API_URL = f'{API_PREFIX}/docs.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "API Documentation",
            'docExpansion': 'none',
            'defaultModelsExpandDepth': -1
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    print(f'📚 Documentación disponible en: http://localhost:{PORT}{API_PREFIX}/docs')