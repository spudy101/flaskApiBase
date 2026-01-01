"""
Base Repository - Generic CRUD operations
Equivalente a src/repository/base.repository.js
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from config.database import db
from src.utils.logger_util import logger

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository con operaciones CRUD genéricas
    Equivalente a BaseRepository en Node.js
    """
    
    def __init__(self, model: type):
        self.model = model
    
    def find_by_id(self, id: str) -> Optional[T]:
        """
        Encuentra por ID
        Equivalente a findById() en Node.js
        """
        try:
            return self.model.query.get(id)
        except SQLAlchemyError as e:
            logger.error(f'Error finding {self.model.__name__} by ID', id=id, error=str(e))
            raise
    
    def find_one(self, **filters) -> Optional[T]:
        """
        Encuentra un registro por filtros
        Equivalente a findOne() en Node.js
        """
        try:
            return self.model.query.filter_by(**filters).first()
        except SQLAlchemyError as e:
            logger.error(f'Error finding one {self.model.__name__}', filters=filters, error=str(e))
            raise
    
    def find_all(self, **filters) -> List[T]:
        """
        Encuentra todos los registros
        Equivalente a findAll() en Node.js
        """
        try:
            if filters:
                return self.model.query.filter_by(**filters).all()
            return self.model.query.all()
        except SQLAlchemyError as e:
            logger.error(f'Error finding all {self.model.__name__}', filters=filters, error=str(e))
            raise
    
    def find_with_pagination(
        self,
        page: int = 1,
        limit: int = 10,
        **filters
    ) -> Dict[str, Any]:
        """
        Encuentra con paginación
        Equivalente a findAndCountAll() en Node.js
        """
        try:
            query = self.model.query
            
            if filters:
                query = query.filter_by(**filters)
            
            pagination = query.paginate(
                page=page,
                per_page=limit,
                error_out=False
            )
            
            return {
                'rows': pagination.items,
                'count': pagination.total,
                'page': page,
                'limit': limit,
                'total_pages': pagination.pages
            }
        except SQLAlchemyError as e:
            logger.error(f'Error paginating {self.model.__name__}', error=str(e))
            raise
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Crea un nuevo registro
        Equivalente a create() en Node.js
        """
        try:
            instance = self.model(**data)
            db.session.add(instance)
            db.session.commit()
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error creating {self.model.__name__}', error=str(e))
            raise
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Actualiza un registro
        Equivalente a update() en Node.js (optimizado con single query)
        """
        try:
            instance = self.find_by_id(id)
            
            if not instance:
                return None
            
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            db.session.commit()
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error updating {self.model.__name__}', id=id, error=str(e))
            raise
    
    def delete(self, id: str) -> bool:
        """
        Elimina un registro
        Equivalente a delete() en Node.js
        """
        try:
            instance = self.find_by_id(id)
            
            if not instance:
                return False
            
            db.session.delete(instance)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error deleting {self.model.__name__}', id=id, error=str(e))
            raise
    
    def count(self, **filters) -> int:
        """Cuenta registros"""
        try:
            if filters:
                return self.model.query.filter_by(**filters).count()
            return self.model.query.count()
        except SQLAlchemyError as e:
            logger.error(f'Error counting {self.model.__name__}', error=str(e))
            raise
    
    def exists(self, **filters) -> bool:
        """Verifica si existe"""
        return self.count(**filters) > 0
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """Crea múltiples registros"""
        try:
            instances = [self.model(**data) for data in data_list]
            db.session.add_all(instances)
            db.session.commit()
            return instances
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error bulk creating {self.model.__name__}', error=str(e))
            raise
