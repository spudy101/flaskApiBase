"""
DTOs package
Exporta todos los DTOs
"""
from .auth_dto import (
    RegisterDTO,
    LoginDTO,
    RefreshTokenDTO,
    UserResponseDTO,
    TokensDTO,
    AuthResponseDTO
)

from .user_dto import UpdateUserDTO

from .product_dto import (
    CreateProductDTO,
    UpdateProductDTO,
    ProductResponseDTO
)

__all__ = [
    # Auth DTOs
    'RegisterDTO',
    'LoginDTO',
    'RefreshTokenDTO',
    'UserResponseDTO',
    'TokensDTO',
    'AuthResponseDTO',
    # User DTOs
    'UpdateUserDTO',
    # Product DTOs
    'CreateProductDTO',
    'UpdateProductDTO',
    'ProductResponseDTO'
]
