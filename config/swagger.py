"""
Configuración de Swagger/OpenAPI
Equivalente a swagger.js
"""
from .swagger_paths.auth import auth_paths
from flask_swagger_ui import get_swaggerui_blueprint
from flask import jsonify
import os


def setup_swagger(app):
    """
    Configurar Swagger UI y documentación OpenAPI
    
    Args:
        app: Instancia de Flask
    """
    API_PREFIX = os.getenv('API_PREFIX', '/api/v1')
    PORT = os.getenv('PORT', '5000')

    all_paths = {}
    all_paths.update(auth_paths)

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
            'schemas': {
                'SuccessResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean', 'example': True},
                        'message': {'type': 'string', 'example': 'Operación exitosa'},
                        'data': {'type': 'object'},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2025-12-18T20:00:00.000Z'}
                    }
                },
                'ErrorResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean', 'example': False},
                        'message': {'type': 'string', 'example': 'Error en la operación'},
                        'timestamp': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'ValidationErrorResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean', 'example': False},
                        'message': {'type': 'string', 'example': 'Errores de validación'},
                        'errors': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'field': {'type': 'string', 'example': 'email'},
                                    'message': {'type': 'string', 'example': 'El email es requerido'}
                                }
                            }
                        },
                        'timestamp': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'PaginatedResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean', 'example': True},
                        'message': {'type': 'string'},
                        'data': {'type': 'array', 'items': {'type': 'object'}},
                        'pagination': {
                            'type': 'object',
                            'properties': {
                                'page': {'type': 'integer', 'example': 1},
                                'limit': {'type': 'integer', 'example': 10},
                                'total': {'type': 'integer', 'example': 100},
                                'totalPages': {'type': 'integer', 'example': 10},
                                'hasNextPage': {'type': 'boolean', 'example': True},
                                'hasPrevPage': {'type': 'boolean', 'example': False}
                            }
                        },
                        'timestamp': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'User': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string', 'format': 'uuid'},
                        'email': {'type': 'string', 'format': 'email', 'example': 'usuario@example.com'},
                        'name': {'type': 'string', 'example': 'Juan Pérez'},
                        'role': {'type': 'string', 'enum': ['user', 'admin'], 'example': 'user'},
                        'isActive': {'type': 'boolean', 'example': True},
                        'lastLogin': {'type': 'string', 'format': 'date-time', 'nullable': True},
                        'createdAt': {'type': 'string', 'format': 'date-time'},
                        'updatedAt': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'Product': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string', 'format': 'uuid'},
                        'name': {'type': 'string', 'example': 'Laptop HP'},
                        'description': {'type': 'string', 'example': 'Laptop HP Pavilion 15.6"'},
                        'price': {'type': 'number', 'format': 'decimal', 'example': 799.99},
                        'stock': {'type': 'integer', 'example': 15},
                        'category': {'type': 'string', 'example': 'Electronics'},
                        'isActive': {'type': 'boolean', 'example': True},
                        'createdBy': {'type': 'string', 'format': 'uuid'},
                        'createdAt': {'type': 'string', 'format': 'date-time'},
                        'updatedAt': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        'tags': [
            {'name': 'Auth', 'description': 'Endpoints de autenticación y gestión de perfil'},
            {'name': 'Users', 'description': 'Gestión de usuarios (Solo Admin)'},
            {'name': 'Products', 'description': 'Gestión de productos (CRUD completo)'}
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