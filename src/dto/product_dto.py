"""
Product DTOs - Data Transfer Objects
Equivalente a src/dto/product.dto.js
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class CreateProductDTO:
    """DTO para creación de producto"""
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    created_by: str  # User ID
    
    @classmethod
    def from_request(cls, data: Dict[str, Any], user_id: str) -> 'CreateProductDTO':
        """Crea DTO desde request data"""
        return cls(
            name=data.get('name', '').strip(),
            description=data.get('description', '').strip() if data.get('description') else None,
            price=float(data.get('price', 0)),
            stock=int(data.get('stock', 0)),
            category=data.get('category', '').strip() if data.get('category') else None,
            created_by=user_id
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UpdateProductDTO:
    """DTO para actualización de producto"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    
    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> 'UpdateProductDTO':
        """Crea DTO desde request data con solo campos proporcionados"""
        dto_data = {}
        
        if 'name' in data:
            dto_data['name'] = data['name'].strip()
        if 'description' in data:
            dto_data['description'] = data['description'].strip() if data['description'] else None
        if 'price' in data:
            dto_data['price'] = float(data['price'])
        if 'stock' in data:
            dto_data['stock'] = int(data['stock'])
        if 'category' in data:
            dto_data['category'] = data['category'].strip() if data['category'] else None
        if 'is_active' in data:
            dto_data['is_active'] = bool(data['is_active'])
        
        return cls(**dto_data)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario solo con campos no-None"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ProductResponseDTO:
    """DTO para respuesta de producto"""
    id: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    is_active: bool
    created_by: str
    created_at: str
    updated_at: str
    creator: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_model(cls, product, include_creator: bool = False) -> 'ProductResponseDTO':
        """Crea DTO desde modelo Product"""
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'category': product.category,
            'is_active': product.is_active,
            'created_by': product.created_by,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }
        
        if include_creator and product.creator:
            data['creator'] = {
                'id': product.creator.id,
                'name': product.creator.name,
                'email': product.creator.email
            }
        
        return cls(**data)
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


__all__ = ['CreateProductDTO', 'UpdateProductDTO', 'ProductResponseDTO']
