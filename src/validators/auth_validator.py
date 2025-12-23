from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
import re
from sqlalchemy import select
from src.models import User


class RegisterSchema(Schema):
    """Schema para validación de registro de usuario"""
    
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'El email es requerido',
            'invalid': 'Debe ser un email válido'
        }
    )
    
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error='La contraseña debe tener al menos 6 caracteres'),
        error_messages={
            'required': 'La contraseña es requerida'
        }
    )
    
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100, error='El nombre debe tener entre 2 y 100 caracteres'),
        error_messages={
            'required': 'El nombre es requerido'
        }
    )
    
    role = fields.String(
        load_default='user',
        validate=validate.OneOf(['user', 'admin'], error='El rol debe ser user o admin')
    )
    
    @validates('password')
    def validate_password(self, value):
        """Validar que la contraseña tenga mayúscula, minúscula y número"""
        if not re.search(r'[a-z]', value):
            raise ValidationError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'\d', value):
            raise ValidationError('La contraseña debe contener al menos un número')
    
    @validates('name')
    def validate_name(self, value):
        """Validar que el nombre solo contenga letras y espacios"""
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(pattern, value):
            raise ValidationError('El nombre solo puede contener letras y espacios')
    
    @validates('email')
    def validate_email_unique(self, value):
        """Validar que el email no esté registrado"""
        from config.database import SessionLocal
        
        db = SessionLocal()
        try:
            stmt = select(User).where(User.email == value.lower())
            existing_user = db.execute(stmt).scalar_one_or_none()
            
            if existing_user:
                raise ValidationError('El email ya está registrado')
        finally:
            db.close()


class LoginSchema(Schema):
    """Schema para validación de login"""
    
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'El email es requerido',
            'invalid': 'Debe ser un email válido'
        }
    )
    
    password = fields.String(
        required=True,
        error_messages={
            'required': 'La contraseña es requerida'
        }
    )


class UpdateProfileSchema(Schema):
    """Schema para validación de actualización de perfil"""
    
    name = fields.String(
        validate=validate.Length(min=2, max=100, error='El nombre debe tener entre 2 y 100 caracteres'),
        allow_none=True
    )
    
    email = fields.Email(
        error_messages={
            'invalid': 'Debe ser un email válido'
        },
        allow_none=True
    )
    
    def __init__(self, current_user_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user_id = current_user_id
    
    @validates('name')
    def validate_name(self, value):
        """Validar que el nombre solo contenga letras y espacios"""
        if value:
            pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
            if not re.match(pattern, value):
                raise ValidationError('El nombre solo puede contener letras y espacios')
    
    @validates('email')
    def validate_email_unique(self, value):
        """Validar que el email no esté en uso por otro usuario"""
        if not value or not self.current_user_id:
            return
        
        from config.database import SessionLocal
        
        db = SessionLocal()
        try:
            stmt = select(User).where(User.email == value.lower())
            existing_user = db.execute(stmt).scalar_one_or_none()
            
            if existing_user and str(existing_user.id) != str(self.current_user_id):
                raise ValidationError('El email ya está en uso por otro usuario')
        finally:
            db.close()


class ChangePasswordSchema(Schema):
    """Schema para validación de cambio de contraseña"""
    
    currentPassword = fields.String(
        required=True,
        error_messages={
            'required': 'La contraseña actual es requerida'
        }
    )
    
    newPassword = fields.String(
        required=True,
        validate=validate.Length(min=6, error='La nueva contraseña debe tener al menos 6 caracteres'),
        error_messages={
            'required': 'La nueva contraseña es requerida'
        }
    )
    
    confirmPassword = fields.String(
        required=True,
        error_messages={
            'required': 'Debes confirmar la nueva contraseña'
        }
    )
    
    @validates('newPassword')
    def validate_new_password(self, value):
        """Validar que la nueva contraseña tenga mayúscula, minúscula y número"""
        if not re.search(r'[a-z]', value):
            raise ValidationError('La nueva contraseña debe contener al menos una minúscula')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('La nueva contraseña debe contener al menos una mayúscula')
        if not re.search(r'\d', value):
            raise ValidationError('La nueva contraseña debe contener al menos un número')
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validar que las contraseñas coincidan y sean diferentes"""
        current = data.get('currentPassword')
        new = data.get('newPassword')
        confirm = data.get('confirmPassword')
        
        # Validar que la nueva contraseña sea diferente
        if current and new and current == new:
            raise ValidationError(
                'La nueva contraseña debe ser diferente a la actual',
                field_name='newPassword'
            )
        
        # Validar que las contraseñas coincidan
        if new and confirm and new != confirm:
            raise ValidationError(
                'Las contraseñas no coinciden',
                field_name='confirmPassword'
            )


# Funciones helper para usar en los controllers
def validate_register(data):
    """
    Valida datos de registro
    
    Args:
        data: Dict con datos de registro
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = RegisterSchema()
    return schema.load(data)


def validate_login(data):
    """
    Valida datos de login
    
    Args:
        data: Dict con datos de login
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = LoginSchema()
    return schema.load(data)


def validate_update_profile(data, current_user_id):
    """
    Valida datos de actualización de perfil
    
    Args:
        data: Dict con datos a actualizar
        current_user_id: ID del usuario actual
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = UpdateProfileSchema(current_user_id=current_user_id)
    return schema.load(data)


def validate_change_password(data):
    """
    Valida datos de cambio de contraseña
    
    Args:
        data: Dict con contraseñas
        
    Returns:
        Dict con datos validados
        
    Raises:
        ValidationError si hay errores
    """
    schema = ChangePasswordSchema()
    return schema.load(data)