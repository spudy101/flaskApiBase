"""
Auth Validators - Request validation
Equivalente a src/validators/auth.validator.js
"""
from functools import wraps
from flask import request
from marshmallow import Schema, fields, validate, ValidationError
from src.utils.response_util import ApiResponse


# ========================================
# Schemas
# ========================================

class RegisterSchema(Schema):
    """Schema para validación de registro"""
    email = fields.Email(required=True, error_messages={'required': 'Email es requerido'})
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=100, error='Password debe tener entre 8 y 100 caracteres'),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])',
                error='Password debe contener al menos: 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial'
            )
        ],
        error_messages={'required': 'Password es requerido'}
    )
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=100, error='Nombre debe tener entre 2 y 100 caracteres'),
            validate.Regexp(
                r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                error='Nombre solo puede contener letras y espacios'
            )
        ],
        error_messages={'required': 'Nombre es requerido'}
    )
    role = fields.Str(
        validate=validate.OneOf(['user', 'admin'], error='Rol debe ser "user" o "admin"'),
        load_default='user'
    )


class LoginSchema(Schema):
    """Schema para validación de login"""
    email = fields.Email(required=True, error_messages={'required': 'Email es requerido'})
    password = fields.Str(required=True, error_messages={'required': 'Password es requerido'})


class RefreshTokenSchema(Schema):
    """Schema para validación de refresh token"""
    refresh_token = fields.Str(required=True, error_messages={'required': 'Refresh token es requerido'})
    # También aceptar refreshToken (camelCase de Node.js)
    refreshToken = fields.Str(load_default=None)


# ========================================
# Decorators de validación
# ========================================

def validate_schema(schema_class):
    """
    Decorator genérico para validar request con marshmallow schema
    Equivalente a express-validator en Node.js
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obtener datos del request
                data = request.get_json()
                
                if not data:
                    return ApiResponse.bad_request('Request body es requerido')
                
                # Validar con schema
                schema = schema_class()
                validated_data = schema.load(data)
                
                # Agregar datos validados al request
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as err:
                # Formatear errores de validación
                errors = []
                for field, messages in err.messages.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            errors.append({
                                'field': field,
                                'message': msg
                            })
                    else:
                        errors.append({
                            'field': field,
                            'message': messages
                        })
                
                return ApiResponse.validation_error('Errores de validación', errors)
        
        return decorated_function
    return decorator


def validate_register():
    """Validator para register endpoint"""
    return validate_schema(RegisterSchema)


def validate_login():
    """Validator para login endpoint"""
    return validate_schema(LoginSchema)


def validate_refresh_token():
    """Validator para refresh token endpoint"""
    return validate_schema(RefreshTokenSchema)
