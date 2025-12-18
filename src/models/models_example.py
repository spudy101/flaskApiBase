from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.connection import db

# Modelo base con timestamps
class BaseModel(db.Model):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)

# EJEMPLO: Usuario
class Usuario(BaseModel):
    __tablename__ = 'usuario'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey('persona.id_persona'), nullable=False)
    id_rol = Column(Integer, ForeignKey('rol.id_rol'), nullable=False)
    id_avatar = Column(Integer, ForeignKey('avatar.id_avatar'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    autentificador = Column(Boolean, default=False)
    
    # Relaciones
    persona = relationship('Persona', back_populates='usuario')
    rol = relationship('Rol', back_populates='usuarios')
    avatar = relationship('Avatar', back_populates='usuarios')

# EJEMPLO: Persona
class Persona(BaseModel):
    __tablename__ = 'persona'
    
    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    run = Column(String(20), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(DateTime)
    correo = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20))
    id_prefijo_telefonico = Column(Integer, ForeignKey('prefijo_telefonico.id_prefijo_telefonico'))
    
    # Relaciones
    usuario = relationship('Usuario', back_populates='persona', uselist=False)
    prefijo_telefonico = relationship('PrefijoTelefonico', back_populates='personas')

# EJEMPLO: Rol
class Rol(BaseModel):
    __tablename__ = 'rol'
    
    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre_rol = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)
    
    # Relaciones
    usuarios = relationship('Usuario', back_populates='rol')

# EJEMPLO: Avatar
class Avatar(BaseModel):
    __tablename__ = 'avatar'
    
    id_avatar = Column(Integer, primary_key=True, autoincrement=True)
    nombre_avatar = Column(String(255), nullable=False)
    descripcion = Column(String(255))
    
    # Relaciones
    usuarios = relationship('Usuario', back_populates='avatar')

# EJEMPLO: PrefijoTelefonico
class PrefijoTelefonico(BaseModel):
    __tablename__ = 'prefijo_telefonico'
    
    id_prefijo_telefonico = Column(Integer, primary_key=True, autoincrement=True)
    prefijo = Column(String(10), unique=True, nullable=False)
    pais = Column(String(100), nullable=False)
    
    # Relaciones
    personas = relationship('Persona', back_populates='prefijo_telefonico')

# Exportar todos los modelos
__all__ = [
    'Usuario',
    'Persona',
    'Rol',
    'Avatar',
    'PrefijoTelefonico'
]
