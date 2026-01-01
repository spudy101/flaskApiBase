"""
Product model - SQLAlchemy
Equivalente a src/models/Product.js
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid


class Product:
    """Product model definition"""
    
    @staticmethod
    def define_model(db):
        """Define Product model with SQLAlchemy"""
        
        class ProductModel(db.Model):
            __tablename__ = 'products'
            
            # Columns
            id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
            name = Column(String(200), nullable=False)
            description = Column(Text, nullable=True)
            price = Column(Numeric(10, 2), nullable=False)
            stock = Column(Integer, default=0, nullable=False)
            category = Column(String(100), nullable=True)
            is_active = Column(Boolean, default=True, nullable=False)
            created_by = Column(String(36), ForeignKey('users.id'), nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            
            # Relationships
            creator = relationship('User', back_populates='products')
            
            # Constraints
            __table_args__ = (
                CheckConstraint('price >= 0', name='check_price_positive'),
                CheckConstraint('stock >= 0', name='check_stock_positive'),
            )
            
            def to_dict(self, include_creator: bool = False) -> dict:
                """
                Convierte el modelo a diccionario
                Equivalente a toJSON() en Sequelize
                """
                data = {
                    'id': self.id,
                    'name': self.name,
                    'description': self.description,
                    'price': float(self.price) if self.price else 0.0,
                    'stock': self.stock,
                    'category': self.category,
                    'is_active': self.is_active,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
                
                if include_creator and self.creator:
                    data['creator'] = {
                        'id': self.creator.id,
                        'name': self.creator.name,
                        'email': self.creator.email
                    }
                    
                return data
            
            def __repr__(self):
                return f'<Product {self.name}>'
        
        return ProductModel
