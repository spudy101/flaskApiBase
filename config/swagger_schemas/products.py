"""
Schemas relacionados con productos
"""

product_schemas = {
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
    },
    'ProductCreate': {
        'type': 'object',
        'required': ['name', 'price', 'stock'],
        'properties': {
            'name': {'type': 'string', 'minLength': 2, 'maxLength': 200, 'example': 'Laptop HP'},
            'description': {'type': 'string', 'maxLength': 1000, 'example': 'Laptop HP Pavilion 15.6"'},
            'price': {'type': 'number', 'format': 'decimal', 'minimum': 0, 'example': 799.99},
            'stock': {'type': 'integer', 'minimum': 0, 'example': 15},
            'category': {'type': 'string', 'example': 'Electronics'},
            'isActive': {'type': 'boolean', 'default': True}
        }
    },
    'ProductUpdate': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 2, 'maxLength': 200},
            'description': {'type': 'string', 'maxLength': 1000},
            'price': {'type': 'number', 'format': 'decimal', 'minimum': 0},
            'stock': {'type': 'integer', 'minimum': 0},
            'category': {'type': 'string'},
            'isActive': {'type': 'boolean'}
        }
    },
    'Category': {
        'type': 'object',
        'properties': {
            'id': {'type': 'string', 'format': 'uuid'},
            'name': {'type': 'string', 'example': 'Electronics'},
            'description': {'type': 'string', 'example': 'Electronic devices'},
            'slug': {'type': 'string', 'example': 'electronics'},
            'createdAt': {'type': 'string', 'format': 'date-time'},
            'updatedAt': {'type': 'string', 'format': 'date-time'}
        }
    }
}