from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from sqlalchemy import select
from src.models import Product


class CreateProductSchema(Schema):
    """Schema para validación de creación de producto"""
    
    name = fields.String(
        required=True,
        validate=validate.Length(min=3, max=200, error='El nombre debe tener entre 3 y 200 caracteres'),
        error_messages={
            'required': 'El nombre es requerido'
        }
    )
    
    description = fields.String(
        allow_none=True,
        validate=validate.Length(max=1000, error='La descripción no puede exceder 1000 caracteres')
    )
    
    price = fields.Decimal(
        required=True,
        as_string=False,
        places=2,
        validate=validate.Range(min=0, error='El precio debe ser un número mayor o igual a 0'),
        error_messages={
            'required': 'El precio es requerido',
            'invalid': 'El precio debe ser un número válido'
        }
    )
    
    stock = fields.Integer(
        required=True,
        validate=validate.Range(min=0, error='El stock debe ser un número entero mayor o igual a 0'),
        error_messages={
            'required': 'El stock es requerido'
        }
    )
    
    category = fields.String(
        allow_none=True,
        validate=validate.Length(max=100, error='La categoría no puede exceder 100 caracteres')
    )
    
    isActive = fields.Boolean(
        load_default=True,
        error_messages={
            'invalid': 'isActive debe ser un valor booleano'
        }
    )
    
    @validates('name')
    def validate_name_unique(self, value):
        """Validar que el nombre del producto sea único"""
        from config.database import SessionLocal
        
        db = SessionLocal()
        try:
            stmt = select(Product).where(Product.name == value)
            existing_product = db.execute(stmt).scalar_one_or_none()
            
            if existing_product:
                raise ValidationError('Ya existe un producto con ese nombre')
        finally:
            db.close()


class UpdateProductSchema(Schema):
    """Schema para validación de actualización de producto"""
    
    name = fields.String(
        validate=validate.Length(min=3, max=200, error='El nombre debe tener entre 3 y 200 caracteres'),
        allow_none=True
    )
    
    description = fields.String(
        allow_none=True,
        validate=validate.Length(max=1000, error='La descripción no puede exceder 1000 caracteres')
    )
    
    price = fields.Decimal(
        as_string=False,
        places=2,
        validate=validate.Range(min=0, error='El precio debe ser un número mayor o igual a 0'),
        allow_none=True
    )
    
    stock = fields.Integer(
        validate=validate.Range(min=0, error='El stock debe ser un número entero mayor o igual a 0'),
        allow_none=True
    )
    
    category = fields.String(
        allow_none=True,
        validate=validate.Length(max=100, error='La categoría no puede exceder 100 caracteres')
    )
    
    isActive = fields.Boolean(
        allow_none=True,
        error_messages={
            'invalid': 'isActive debe ser un valor booleano'
        }
    )
    
    def __init__(self, product_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id = product_id
    
    @validates('name')
    def validate_name_unique(self, value):
        """Validar que el nombre no esté usado por otro producto"""
        if not value or not self.product_id:
            return
        
        from config.database import SessionLocal
        
        db = SessionLocal()
        try:
            stmt = select(Product).where(Product.name == value)
            existing_product = db.execute(stmt).scalar_one_or_none()
            
            if existing_product and str(existing_product.id) != str(self.product_id):
                raise ValidationError('Ya existe otro producto con ese nombre')
        finally:
            db.close()


class ProductIdParamSchema(Schema):
    """Schema para validar ID de producto en parámetros"""
    id = fields.UUID(
        required=True,
        error_messages={
            'required': 'El ID del producto es requerido',
            'invalid': 'El ID debe ser un UUID válido'
        }
    )


class ListProductsSchema(Schema):
    """Schema para validación de listado de productos con filtros"""
    
    page = fields.Integer(
        load_default=1,
        validate=validate.Range(min=1, error='La página debe ser un número mayor a 0')
    )
    
    limit = fields.Integer(
        load_default=10,
        validate=validate.Range(min=1, max=100, error='El límite debe estar entre 1 y 100')
    )
    
    category = fields.String(allow_none=True)
    
    isActive = fields.Boolean(
        allow_none=True,
        error_messages={
            'invalid': 'isActive debe ser un valor booleano'
        }
    )
    
    minPrice = fields.Decimal(
        as_string=False,
        places=2,
        validate=validate.Range(min=0, error='El precio mínimo debe ser mayor o igual a 0'),
        allow_none=True
    )
    
    maxPrice = fields.Decimal(
        as_string=False,
        places=2,
        validate=validate.Range(min=0, error='El precio máximo debe ser mayor o igual a 0'),
        allow_none=True
    )
    
    search = fields.String(
        allow_none=True,
        validate=validate.Length(min=2, error='El término de búsqueda debe tener al menos 2 caracteres')
    )
    
    @validates_schema
    def validate_price_range(self, data, **kwargs):
        """Validar que el precio máximo sea mayor al mínimo"""
        min_price = data.get('minPrice')
        max_price = data.get('maxPrice')
        
        if min_price and max_price and max_price < min_price:
            raise ValidationError(
                'El precio máximo debe ser mayor al precio mínimo',
                field_name='maxPrice'
            )


class UpdateStockSchema(Schema):
    """Schema para validación de actualización de stock"""
    
    quantity = fields.Integer(
        required=True,
        error_messages={
            'required': 'La cantidad es requerida',
            'invalid': 'La cantidad debe ser un número entero'
        }
    )
    
    operation = fields.String(
        required=True,
        validate=validate.OneOf(
            ['add', 'subtract', 'set'],
            error='La operación debe ser add, subtract o set'
        ),
        error_messages={
            'required': 'La operación es requerida'
        }
    )


# Funciones helper para usar en los controllers
def validate_create_product(data):
    """
    Valida datos para crear producto
    
    Args:
        data: Dict con datos del producto
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = CreateProductSchema()
    return schema.load(data)


def validate_update_product(data, product_id):
    """
    Valida datos para actualizar producto
    
    Args:
        data: Dict con datos a actualizar
        product_id: ID del producto a actualizar
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = UpdateProductSchema(product_id=product_id)
    return schema.load(data)


def validate_product_id(product_id):
    """
    Valida ID de producto
    
    Args:
        product_id: ID a validar
        
    Returns:
        Dict con id validado
        
    Raises:
        ValidationError si hay errores
    """
    schema = ProductIdParamSchema()
    return schema.load({'id': product_id})


def validate_list_products(query_params):
    """
    Valida parámetros de listado de productos
    
    Args:
        query_params: request.args
        
    Returns:
        Dict con parámetros validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = ListProductsSchema()
    return schema.load(query_params)


def validate_update_stock(data):
    """
    Valida datos de actualización de stock
    
    Args:
        data: Dict con quantity y operation
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = UpdateStockSchema()
    return schema.load(data)