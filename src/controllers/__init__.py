"""
Controllers package
"""
from .auth_controller import AuthController, auth_controller
from .user_controller import UserController, user_controller
from .product_controller import ProductController, product_controller

__all__ = [
    'AuthController',
    'auth_controller',
    'UserController',
    'user_controller',
    'ProductController',
    'product_controller'
]
