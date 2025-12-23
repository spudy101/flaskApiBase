"""
Paths para Auth - Ahora usando referencias a schemas
"""

auth_paths = {
    '/auth/register': {
        'post': {
            'tags': ['Auth'],
            'summary': 'Registrar nuevo usuario',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/UserCreate'}
                    }
                }
            },
            'responses': {
                '201': {
                    'description': 'Usuario registrado exitosamente',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/AuthResponse'}
                        }
                    }
                },
                '400': {
                    'description': 'Error de validación',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/ValidationErrorResponse'}
                        }
                    }
                },
                '429': {'description': 'Demasiadas peticiones'}
            }
        }
    },
    '/auth/login': {
        'post': {
            'tags': ['Auth'],
            'summary': 'Iniciar sesión',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/LoginRequest'}
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Login exitoso',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/AuthResponse'}
                        }
                    }
                },
                '401': {
                    'description': 'Credenciales inválidas',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/ErrorResponse'}
                        }
                    }
                }
            }
        }
    }
}