"""
Definición de paths para Auth
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
                        'schema': {
                            'type': 'object',
                            'required': ['email', 'password', 'name'],
                            'properties': {
                                'email': {'type': 'string', 'format': 'email', 'example': 'usuario@example.com'},
                                'password': {'type': 'string', 'format': 'password', 'minLength': 6, 'example': 'Password123'},
                                'name': {'type': 'string', 'minLength': 2, 'maxLength': 100, 'example': 'Juan Pérez'},
                                'role': {'type': 'string', 'enum': ['user', 'admin'], 'default': 'user'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '201': {
                    'description': 'Usuario registrado exitosamente',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'success': {'type': 'boolean', 'example': True},
                                    'message': {'type': 'string', 'example': 'Usuario registrado exitosamente'},
                                    'data': {
                                        'type': 'object',
                                        'properties': {
                                            'user': {'$ref': '#/components/schemas/User'},
                                            'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                '400': {
                    'description': 'Error de validación',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ValidationErrorResponse'}}}
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
                        'schema': {
                            'type': 'object',
                            'required': ['email', 'password'],
                            'properties': {
                                'email': {'type': 'string', 'format': 'email', 'example': 'usuario@example.com'},
                                'password': {'type': 'string', 'format': 'password', 'example': 'Password123'}
                            }
                        }
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Login exitoso',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'success': {'type': 'boolean', 'example': True},
                                    'message': {'type': 'string', 'example': 'Login exitoso'},
                                    'data': {
                                        'type': 'object',
                                        'properties': {
                                            'user': {'$ref': '#/components/schemas/User'},
                                            'token': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                '401': {
                    'description': 'Credenciales inválidas',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}}
                }
            }
        }
    }
}