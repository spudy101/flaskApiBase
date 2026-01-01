"""
User model - SQLAlchemy
Equivalente a src/models/User.js
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import enum


class UserRole(enum.Enum):
    """User roles enum"""
    USER = 'user'
    ADMIN = 'admin'


class User:
    """
    User model
    Equivalente a Sequelize User model en Node.js
    """
    
    # SQLAlchemy declarative - se definirá en db.Model
    __tablename__ = 'users'
    
    def __init__(self, db_model):
        """Initialize with db.Model base"""
        self.Model = db_model
    
    @staticmethod
    def define_model(db):
        """Define User model with SQLAlchemy"""
        
        class UserModel(db.Model):
            __tablename__ = 'users'
            
            # Columns
            id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
            email = Column(String(255), unique=True, nullable=False, index=True)
            password = Column(String(255), nullable=False)
            name = Column(String(100), nullable=False)
            role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
            is_active = Column(Boolean, default=True, nullable=False)
            last_login = Column(DateTime, nullable=True)
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            
            # Relationships
            products = relationship('Product', back_populates='creator', lazy='dynamic')
            
            def __init__(self, **kwargs):
                """Constructor - hashea password automáticamente"""
                super(UserModel, self).__init__(**kwargs)
                if 'password' in kwargs and kwargs['password']:
                    self.set_password(kwargs['password'])
            
            def set_password(self, password: str) -> None:
                """
                Hashea y establece la contraseña
                Equivalente al hook beforeCreate/beforeUpdate en Sequelize
                """
                self.password = generate_password_hash(password, method='pbkdf2:sha256')
            
            def check_password(self, password: str) -> bool:
                """
                Verifica si la contraseña es correcta
                Equivalente a comparePassword en Node
                """
                return check_password_hash(self.password, password)
            
            def to_dict(self, exclude_password: bool = True) -> dict:
                """
                Convierte el modelo a diccionario
                Equivalente a toJSON() en Sequelize
                """
                data = {
                    'id': self.id,
                    'email': self.email,
                    'name': self.name,
                    'role': self.role.value if isinstance(self.role, UserRole) else self.role,
                    'is_active': self.is_active,
                    'last_login': self.last_login.isoformat() if self.last_login else None,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None
                }
                
                if not exclude_password:
                    data['password'] = self.password
                    
                return data
            
            def __repr__(self):
                return f'<User {self.email}>'
        
        return UserModel
