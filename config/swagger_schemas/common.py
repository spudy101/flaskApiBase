"""
Schemas comunes reutilizables
"""

common_schemas = {
    'SuccessResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'message': {'type': 'string', 'example': 'Operación exitosa'},
            'data': {'type': 'object'},
            'timestamp': {'type': 'string', 'format': 'date-time'}
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
    }
}