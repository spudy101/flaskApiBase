"""
LoginAttempt model - SQLAlchemy
Equivalente a src/models/LoginAttempts.js
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
import uuid


class LoginAttempt:
    """LoginAttempt model definition"""
    
    @staticmethod
    def define_model(db):
        """Define LoginAttempt model with SQLAlchemy"""
        
        class LoginAttemptModel(db.Model):
            __tablename__ = 'login_attempts'
            
            # Columns
            id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
            email = Column(String(255), nullable=False, index=True)
            ip_address = Column(String(45), nullable=True)
            attempts = Column(Integer, default=0, nullable=False)
            blocked_until = Column(DateTime, nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            
            def to_dict(self) -> dict:
                """Convierte el modelo a diccionario"""
                return {
                    'id': self.id,
                    'email': self.email,
                    'ip_address': self.ip_address,
                    'attempts': self.attempts,
                    'blocked_until': self.blocked_until.isoformat() if self.blocked_until else None,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
            
            def __repr__(self):
                return f'<LoginAttempt {self.email} - {self.attempts} attempts>'
        
        return LoginAttemptModel
