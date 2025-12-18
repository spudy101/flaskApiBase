import os
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger

def setup_swagger(app: Flask):
    """
    Configura Swagger UI para documentación de API
    Equivalente a setupSwagger() de Node.js
    """
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api-docs/",
        "title": "API RESTful Flask",
        "version": "1.0.0",
        "description": "Documentación de la API RESTful en Flask",
        "termsOfService": "",
        "contact": {
            "email": "support@example.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API RESTful",
            "version": "1.0.0",
            "description": "Documentación de la API RESTful",
        },
        "host": os.getenv('API_URL', 'localhost:5000').replace('http://', '').replace('https://', ''),
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header usando el esquema Bearer. Ejemplo: 'Bearer {token}'"
            },
            "Cookie": {
                "type": "apiKey",
                "name": "jwtToken",
                "in": "cookie",
                "description": "JWT Token almacenado en cookie"
            }
        },
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    print("📚 Swagger UI disponible en: http://localhost:5000/api-docs/")
    
    return swagger

__all__ = ['setup_swagger']
