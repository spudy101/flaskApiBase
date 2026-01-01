"""
Repositories package
"""
from .base_repository import BaseRepository
from .user_repository import UserRepository, user_repository
from .product_repository import ProductRepository, product_repository
from .login_attempts_repository import LoginAttemptsRepository, login_attempts_repository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'user_repository',
    'ProductRepository',
    'product_repository',
    'LoginAttemptsRepository',
    'login_attempts_repository'
]
