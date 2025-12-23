"""
Schemas relacionados con autenticación y usuarios
"""

auth_schemas = {
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
    'UserCreate': {
        'type': 'object',
        'required': ['email', 'password', 'name'],
        'properties': {
            'email': {'type': 'string', 'format': 'email', 'example': 'usuario@example.com'},
            'password': {'type': 'string', 'format': 'password', 'minLength': 6, 'example': 'Password123'},
            'name': {'type': 'string', 'minLength': 2, 'maxLength': 100, 'example': 'Juan Pérez'},
            'role': {'type': 'string', 'enum': ['user', 'admin'], 'default': 'user'}
        }
    },
    'LoginRequest': {
        'type': 'object',
        'required': ['email', 'password'],
        'properties': {
            'email': {'type': 'string', 'format': 'email', 'example': 'usuario@example.com'},
            'password': {'type': 'string', 'format': 'password', 'example': 'Password123'}
        }
    },
    'AuthResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'message': {'type': 'string'},
            'data': {
                'type': 'object',
                'properties': {
                    'user': {'$ref': '#/components/schemas/User'},
                    'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'}
                }
            },
            'timestamp': {'type': 'string', 'format': 'date-time'}
        }
    }
}