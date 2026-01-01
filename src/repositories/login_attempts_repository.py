"""
LoginAttempts Repository
Equivalente a src/repository/loginAttempts.repository.js
"""
from typing import Optional
from datetime import datetime, timedelta
from src.models import LoginAttempt
from src.repositories.base_repository import BaseRepository
from config.database import db


class LoginAttemptsRepository(BaseRepository[LoginAttempt]):
    """LoginAttempts repository"""
    
    MAX_ATTEMPTS = 5
    BLOCK_DURATION_MINUTES = 15
    
    def __init__(self):
        super().__init__(LoginAttempt)
    
    def find_by_email(self, email: str) -> Optional[LoginAttempt]:
        """Encuentra record por email"""
        return self.find_one(email=email)
    
    def is_blocked(self, email: str) -> bool:
        """Verifica si el email está bloqueado"""
        record = self.find_by_email(email)
        
        if not record or not record.blocked_until:
            return False
        
        return datetime.utcnow() < record.blocked_until
    
    def get_remaining_block_time(self, email: str) -> int:
        """Retorna segundos restantes de bloqueo"""
        record = self.find_by_email(email)
        
        if not record or not record.blocked_until:
            return 0
        
        remaining = (record.blocked_until - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
    
    def increment_attempts(self, email: str, ip_address: str) -> LoginAttempt:
        """Incrementa intentos de login"""
        record = self.find_by_email(email)
        
        if not record:
            # Crear nuevo record
            record = self.create({
                'email': email,
                'ip_address': ip_address,
                'attempts': 1
            })
        else:
            # Incrementar
            record.attempts += 1
            record.ip_address = ip_address
            
            # Bloquear si excede max attempts
            if record.attempts >= self.MAX_ATTEMPTS:
                record.blocked_until = datetime.utcnow() + timedelta(minutes=self.BLOCK_DURATION_MINUTES)
            
            db.session.commit()
        
        return record
    
    def reset_attempts(self, email: str) -> bool:
        """Resetea intentos después de login exitoso"""
        record = self.find_by_email(email)
        
        if not record:
            return False
        
        record.attempts = 0
        record.blocked_until = None
        db.session.commit()
        return True


# Singleton instance
login_attempts_repository = LoginAttemptsRepository()
