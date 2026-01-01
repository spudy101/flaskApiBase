"""
Product Repository
Equivalente a src/repository/product.repository.js
"""
from typing import List, Dict, Any
from src.models import Product
from src.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Product repository"""
    
    def __init__(self):
        super().__init__(Product)
    
    def find_by_category(self, category: str) -> List[Product]:
        """Encuentra productos por categoría"""
        return self.find_all(category=category, is_active=True)
    
    def find_by_creator(self, user_id: str) -> List[Product]:
        """Encuentra productos de un usuario"""
        return self.find_all(created_by=user_id)
    
    def find_active(self) -> List[Product]:
        """Encuentra productos activos"""
        return self.find_all(is_active=True)
    
    def soft_delete(self, product_id: str) -> bool:
        """Soft delete (marca como inactivo)"""
        return self.update(product_id, {'is_active': False}) is not None
    
    def search_by_name(self, search_term: str) -> List[Product]:
        """Busca productos por nombre"""
        return Product.query.filter(
            Product.name.ilike(f'%{search_term}%'),
            Product.is_active == True
        ).all()


# Singleton instance
product_repository = ProductRepository()
