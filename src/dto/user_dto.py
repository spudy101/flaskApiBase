"""
User DTOs - Data Transfer Objects
Equivalente a src/dto/user.dto.js
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class UpdateUserDTO:
    """
    DTO para actualización de usuario
    Todos los campos son opcionales
    """
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> 'UpdateUserDTO':
        """
        Crea DTO desde request data
        Solo incluye campos proporcionados
        """
        dto_data = {}
        
        if 'name' in data:
            name = data.get('name', '')
            dto_data['name'] = name.strip() if name else ''
        
        if 'email' in data:
            email = data.get('email', '')
            dto_data['email'] = email.lower().strip() if email else ''
        
        if 'password' in data:
            dto_data['password'] = data.get('password', '')
        
        return cls(**dto_data)
    
    def to_dict(self) -> dict:
        """
        Convierte a diccionario solo con campos no-None
        """
        return {k: v for k, v in asdict(self).items() if v is not None}


# UserResponseDTO ya está en auth_dto.py, pero lo re-exportamos aquí por conveniencia
from .auth_dto import UserResponseDTO

__all__ = ['UpdateUserDTO', 'UserResponseDTO']
