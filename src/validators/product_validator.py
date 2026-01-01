"""
Product Validators
Validación de requests de productos
"""
from functools import wraps
from flask import request
from marshmallow import Schema, fields, validate, ValidationError
from src.utils.response_util import ApiResponse


class CreateProductSchema(Schema):
    """Schema para crear producto"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200, error='Nombre debe tener entre 3 y 200 caracteres'),
        error_messages={'required': 'Nombre es requerido'}
    )
    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=1000, error='Descripción no puede exceder 1000 caracteres')
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0, error='Precio debe ser mayor o igual a 0'),
        error_messages={'required': 'Precio es requerido'}
    )
    stock = fields.Int(
        required=True,
        validate=validate.Range(min=0, error='Stock debe ser mayor o igual a 0'),
        error_messages={'required': 'Stock es requerido'}
    )
    category = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error='Categoría no puede exceder 100 caracteres')
    )


class UpdateProductSchema(Schema):
    """Schema para actualizar producto"""
    name = fields.Str(
        validate=validate.Length(min=3, max=200, error='Nombre debe tener entre 3 y 200 caracteres')
    )
    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=1000, error='Descripción no puede exceder 1000 caracteres')
    )
    price = fields.Float(
        validate=validate.Range(min=0, error='Precio debe ser mayor o igual a 0')
    )
    stock = fields.Int(
        validate=validate.Range(min=0, error='Stock debe ser mayor o igual a 0')
    )
    category = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error='Categoría no puede exceder 100 caracteres')
    )
    is_active = fields.Bool()


def validate_schema(schema_class):
    """Decorator genérico de validación"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                
                if not data:
                    return ApiResponse.bad_request('Request body es requerido')
                
                schema = schema_class()
                validated_data = schema.load(data)
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as err:
                errors = []
                for field, messages in err.messages.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            errors.append({'field': field, 'message': msg})
                    else:
                        errors.append({'field': field, 'message': messages})
                
                return ApiResponse.validation_error('Errores de validación', errors)
        
        return decorated_function
    return decorator


def validate_create_product():
    """Validator para crear producto"""
    return validate_schema(CreateProductSchema)


def validate_update_product():
    """Validator para actualizar producto"""
    return validate_schema(UpdateProductSchema)
