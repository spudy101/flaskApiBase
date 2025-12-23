from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from datetime import datetime
from typing import List


class UUIDParamSchema(Schema):
    """Schema para validar UUID en parámetros de ruta"""
    id = fields.UUID(required=True, error_messages={
        'required': 'El id es requerido',
        'invalid': 'El id debe ser un UUID válido'
    })


class CustomUUIDParamSchema(Schema):
    """Schema flexible para validar UUID con nombre personalizado"""
    def __init__(self, param_name='id', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[param_name] = fields.UUID(
            required=True,
            error_messages={
                'required': f'El {param_name} es requerido',
                'invalid': f'El {param_name} debe ser un UUID válido'
            }
        )


class PaginationSchema(Schema):
    """Schema para validación de paginación"""
    page = fields.Integer(
        load_default=1,
        validate=validate.Range(min=1, error='La página debe ser un número mayor a 0')
    )
    limit = fields.Integer(
        load_default=10,
        validate=validate.Range(min=1, max=100, error='El límite debe estar entre 1 y 100')
    )


class SortSchema(Schema):
    """
    Schema para validación de ordenamiento
    
    Uso:
        schema = SortSchema(allowed_fields=['name', 'created_at', 'price'])
        result = schema.load(request.args)
    """
    sortBy = fields.String(load_default=None)
    sortOrder = fields.String(
        load_default='DESC',
        validate=validate.OneOf(
            ['ASC', 'DESC', 'asc', 'desc'],
            error='El orden debe ser ASC o DESC'
        )
    )
    
    def __init__(self, allowed_fields: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_fields = allowed_fields or []
    
    @validates_schema
    def validate_sort_by(self, data, **kwargs):
        sort_by = data.get('sortBy')
        if sort_by and self.allowed_fields and sort_by not in self.allowed_fields:
            raise ValidationError(
                f"El campo de ordenamiento debe ser uno de: {', '.join(self.allowed_fields)}",
                field_name='sortBy'
            )


class SearchSchema(Schema):
    """Schema para validación de búsqueda"""
    search = fields.String(
        load_default=None,
        validate=validate.Length(
            min=2,
            max=100,
            error='El término de búsqueda debe tener entre 2 y 100 caracteres'
        )
    )


class DateRangeSchema(Schema):
    """Schema para validación de rango de fechas"""
    startDate = fields.DateTime(
        load_default=None,
        format='iso',
        error_messages={
            'invalid': 'La fecha de inicio debe ser una fecha válida (ISO 8601)'
        }
    )
    endDate = fields.DateTime(
        load_default=None,
        format='iso',
        error_messages={
            'invalid': 'La fecha de fin debe ser una fecha válida (ISO 8601)'
        }
    )
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                'La fecha de fin debe ser posterior a la fecha de inicio',
                field_name='endDate'
            )


class PaginationWithSearchSchema(PaginationSchema, SearchSchema):
    """Combina paginación y búsqueda"""
    pass


class FullQuerySchema(PaginationSchema, SearchSchema, DateRangeSchema):
    """
    Schema completo que combina paginación, búsqueda y rango de fechas
    Útil para endpoints de listado completos
    """
    sortBy = fields.String(load_default=None)
    sortOrder = fields.String(
        load_default='DESC',
        validate=validate.OneOf(['ASC', 'DESC', 'asc', 'desc'])
    )


# Funciones helper para validación en Flask
def validate_uuid_param(param_name='id'):
    """
    Retorna un schema para validar UUID en parámetros
    
    Uso en routes:
        @app.route('/users/<id>')
        def get_user(id):
            schema = validate_uuid_param('id')
            errors = schema.validate({'id': id})
            if errors:
                return error_response('Validación fallida', 400, errors)
    """
    return UUIDParamSchema()


def validate_pagination(query_params):
    """
    Valida parámetros de paginación
    
    Args:
        query_params: request.args
        
    Returns:
        Dict con page y limit validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = PaginationSchema()
    return schema.load(query_params)


def validate_sort(query_params, allowed_fields=None):
    """
    Valida parámetros de ordenamiento
    
    Args:
        query_params: request.args
        allowed_fields: Lista de campos permitidos para ordenar
        
    Returns:
        Dict con sortBy y sortOrder validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = SortSchema(allowed_fields=allowed_fields)
    return schema.load(query_params)


def validate_search(query_params):
    """
    Valida parámetros de búsqueda
    
    Args:
        query_params: request.args
        
    Returns:
        Dict con search validado
        
    Raises:
        ValidationError si hay errores
    """
    schema = SearchSchema()
    return schema.load(query_params)


def validate_date_range(query_params):
    """
    Valida rango de fechas
    
    Args:
        query_params: request.args
        
    Returns:
        Dict con startDate y endDate validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = DateRangeSchema()
    return schema.load(query_params)