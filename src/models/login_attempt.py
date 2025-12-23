import os
from config.database import db
from src.models.base import BaseModel

DB_SCHEMA = os.getenv('DB_SCHEMA')

class LoginAttempt(BaseModel):
    """
    Modelo de Intentos de Login
    """
    __tablename__ = 'login_attempts'
    __table_args__ = {'schema': DB_SCHEMA}
    
    email = db.Column(db.String(255), nullable=False, index=True)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # 45 para IPv6
    
    def __repr__(self):
        return f"<LoginAttempt {self.email} - {self.attempts} intentos>"