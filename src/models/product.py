import os
from config.database import db
from src.models.base import BaseModel
from sqlalchemy.orm import validates
from decimal import Decimal

DB_SCHEMA = os.getenv('DB_SCHEMA')

class Product(BaseModel):
    """
    Modelo de Producto
    Equivalente a Product.js de Sequelize
    """
    __tablename__ = 'products'
    __table_args__ = {'schema': DB_SCHEMA}
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Foreign Key
    created_by = db.Column(
        db.String(36),
        db.ForeignKey(f'{DB_SCHEMA}.users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Relación (belongsTo User)
    creator = db.relationship('User', back_populates='products')
    
    # Validaciones
    @validates('name')
    def validate_name(self, key, name):
        """Valida nombre del producto"""
        if not name or len(name.strip()) == 0:
            raise ValueError('El nombre es requerido')
        
        if len(name) < 3 or len(name) > 200:
            raise ValueError('El nombre debe tener entre 3 y 200 caracteres')
        
        return name.strip()
    
    @validates('price')
    def validate_price(self, key, price):
        """Valida precio"""
        if price is None:
            raise ValueError('El precio es requerido')
        
        price_decimal = Decimal(str(price))
        
        if price_decimal < 0:
            raise ValueError('El precio debe ser mayor o igual a 0')
        
        return price_decimal
    
    @validates('stock')
    def validate_stock(self, key, stock):
        """Valida stock"""
        if stock is None:
            raise ValueError('El stock es requerido')
        
        if not isinstance(stock, int):
            raise ValueError('El stock debe ser un número entero')
        
        if stock < 0:
            raise ValueError('El stock debe ser mayor o igual a 0')
        
        return stock