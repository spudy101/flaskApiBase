"""
Auth DTOs - Data Transfer Objects
Equivalente a src/dto/auth.dto.js
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


# ========================================
# INPUT DTOs (Request - datos entrantes)
# ========================================

@dataclass
class RegisterDTO:
    """
    DTO para registro de usuario
    Equivalente a RegisterDTO en Node.js
    """
    email: str
    password: str
    name: str
    role: str = 'user'
    
    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> 'RegisterDTO':
        """
        Crea DTO desde request data con sanitización
        Equivalente a fromRequest() en Node.js
        """
        email = data.get('email', '')
        name = data.get('name', '')
        
        return cls(
            email=email.lower().strip() if email else '',
            password=data.get('password', ''),
            name=name.strip() if name else '',
            role=data.get('role', 'user')
        )
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return asdict(self)


@dataclass
class LoginDTO:
    """
    DTO para login de usuario
    Equivalente a LoginDTO en Node.js
    """
    email: str
    password: str
    
    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> 'LoginDTO':
        """Crea DTO desde request data con sanitización"""
        email = data.get('email', '')
        
        return cls(
            email=email.lower().strip() if email else '',
            password=data.get('password', '')
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RefreshTokenDTO:
    """
    DTO para refresh token
    Equivalente a RefreshTokenDTO en Node.js
    """
    refresh_token: str
    
    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> 'RefreshTokenDTO':
        """
        Crea DTO desde request data
        Soporta ambos formatos: refresh_token y refreshToken
        """
        token = data.get('refresh_token', data.get('refreshToken', ''))
        return cls(refresh_token=token)
    
    def to_dict(self) -> dict:
        return asdict(self)


# ========================================
# OUTPUT DTOs (Response - datos salientes)
# ========================================

@dataclass
class UserResponseDTO:
    """
    DTO para respuesta de usuario (sin password)
    Equivalente a UserResponseDTO en Node.js
    """
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_model(cls, user) -> 'UserResponseDTO':
        """
        Crea DTO desde modelo User
        Excluye password automáticamente
        """
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            is_active=user.is_active,
            last_login=user.last_login.isoformat() if user.last_login else None,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )
    
    def to_dict(self) -> dict:
        """
        Convierte a diccionario excluyendo None values opcionales
        Mantiene is_active aunque sea False
        """
        data = asdict(self)
        # Remover Nones opcionales pero mantener is_active
        return {k: v for k, v in data.items() if v is not None or k == 'is_active'}


@dataclass
class TokensDTO:
    """
    DTO para tokens (access + refresh)
    Equivalente a TokenResponseDTO en Node.js
    """
    access_token: str
    refresh_token: str
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }


@dataclass
class AuthResponseDTO:
    """
    DTO para respuesta de autenticación completa (user + tokens)
    Equivalente a AuthResponseDTO en Node.js
    """
    user: UserResponseDTO
    tokens: TokensDTO
    
    @classmethod
    def from_data(cls, user, tokens: dict) -> 'AuthResponseDTO':
        """
        Crea DTO desde user model y tokens dict
        """
        return cls(
            user=UserResponseDTO.from_model(user),
            tokens=TokensDTO(
                access_token=tokens.get('access_token', tokens.get('accessToken', '')),
                refresh_token=tokens.get('refresh_token', tokens.get('refreshToken', ''))
            )
        )
    
    def to_dict(self) -> dict:
        """Convierte a diccionario nested"""
        return {
            'user': self.user.to_dict(),
            'tokens': self.tokens.to_dict()
        }
