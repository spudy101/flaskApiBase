"""
User Repository
Equivalente a src/repository/user.repository.js
"""
from typing import Optional
from datetime import datetime
from src.models import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User repository con métodos específicos
    Equivalente a UserRepository en Node.js
    """
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Encuentra usuario por email
        Equivalente a findByEmail() en Node.js
        """
        return self.find_one(email=email)
    
    def find_active_by_email(self, email: str) -> Optional[User]:
        """
        Encuentra usuario activo por email
        Equivalente a findActiveByEmail() en Node.js
        """
        return self.find_one(email=email, is_active=True)
    
    def update_last_login(self, user_id: str) -> bool:
        """
        Actualiza last_login del usuario
        Equivalente a updateLastLogin() en Node.js
        """
        user = self.find_by_id(user_id)
        if not user:
            return False
        
        user.last_login = datetime.utcnow()
        from config.database import db
        db.session.commit()
        return True
    
    def deactivate(self, user_id: str) -> bool:
        """Desactiva un usuario (soft delete)"""
        return self.update(user_id, {'is_active': False}) is not None


# Singleton instance
user_repository = UserRepository()
