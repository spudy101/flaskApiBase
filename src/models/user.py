import os
from config.database import db
from src.models.base import BaseModel
from sqlalchemy.orm import validates
from sqlalchemy import event
import bcrypt
import re

DB_SCHEMA = os.getenv('DB_SCHEMA')

class User(BaseModel):
    """
    Modelo de Usuario
    Equivalente a User.js de Sequelize
    """
    __tablename__ = 'users'
    __table_args__ = {'schema': DB_SCHEMA}
    
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(
        db.Enum('user', 'admin', name='user_roles'),
        default='user',
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relación con productos
    products = db.relationship('Product', back_populates='creator', lazy='dynamic')
    
    # Validaciones (equivalente a validate en Sequelize)
    @validates('email')
    def validate_email(self, key, email):
        """Valida formato de email"""
        if not email:
            raise ValueError('El email es requerido')
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError('Debe ser un email válido')
        
        return email.lower()
    
    @validates('password')
    def validate_password(self, key, password):
        """Valida longitud de password (antes de hashear)"""
        if not password:
            raise ValueError('La contraseña es requerida')
        
        # Solo valida longitud si NO está hasheada (no empieza con $2b$)
        if not password.startswith('$2b$'):
            if len(password) < 6 or len(password) > 100:
                raise ValueError('La contraseña debe tener entre 6 y 100 caracteres')
        
        return password
    
    @validates('name')
    def validate_name(self, key, name):
        """Valida nombre"""
        if not name or len(name.strip()) == 0:
            raise ValueError('El nombre es requerido')
        
        if len(name) < 2 or len(name) > 100:
            raise ValueError('El nombre debe tener entre 2 y 100 caracteres')
        
        return name.strip()
    
    @validates('role')
    def validate_role(self, key, role):
        """Valida rol"""
        valid_roles = ['user', 'admin']
        if role not in valid_roles:
            raise ValueError(f'El rol debe ser {" o ".join(valid_roles)}')
        
        return role
    
    def set_password(self, password):
        """
        Hashea la contraseña
        Equivalente a beforeCreate/beforeUpdate hooks
        """
        if password:
            salt = bcrypt.gensalt()
            self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def compare_password(self, candidate_password):
        """
        Compara contraseña (método de instancia)
        Equivalente a User.prototype.comparePassword
        """
        return bcrypt.checkpw(
            candidate_password.encode('utf-8'),
            self.password.encode('utf-8')
        )
    
    def to_dict(self, exclude=None):
        """
        Override para excluir password por defecto
        Equivalente a toJSON en Sequelize
        """
        if exclude is None:
            exclude = ['password']
        elif 'password' not in exclude:
            exclude.append('password')
        
        return super().to_dict(exclude=exclude)


# Hooks para hashear password automáticamente
# Equivalente a beforeCreate y beforeUpdate de Sequelize
@event.listens_for(User, 'before_insert')
def hash_password_before_insert(mapper, connection, target):
    """Hook antes de insertar - hashea password"""
    if target.password and not target.password.startswith('$2b$'):
        target.set_password(target.password)


@event.listens_for(User, 'before_update')
def hash_password_before_update(mapper, connection, target):
    """Hook antes de actualizar - hashea password solo si cambió"""
    history = db.inspect(target).attrs.password.history
    
    if history.has_changes():
        new_password = target.password
        if new_password and not new_password.startswith('$2b$'):
            target.set_password(new_password)