"""
Rutas de autenticación
Equivalente a authRoutes.js
"""

from flask import Blueprint, request
from src.controllers import AuthController
from src.middlewares import authenticate, validate_request
from src.validators import (
    validate_register,
    validate_login,
    validate_update_profile,
    validate_change_password
)

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

# Instanciar controller
auth_controller = AuthController()


@auth_bp.route('/register', methods=['POST'])
@validate_request(validate_register)
def register():
    """
    Registrar nuevo usuario
    POST /api/v1/auth/register
    """
    return auth_controller.register(request)


@auth_bp.route('/login', methods=['POST'])
@validate_request(validate_login)
def login():
    """
    Login de usuario
    POST /api/v1/auth/login
    """
    return auth_controller.login(request)


@auth_bp.route('/profile', methods=['GET'])
@authenticate
def get_profile():
    """
    Obtener perfil del usuario autenticado
    GET /api/v1/auth/profile
    """
    return auth_controller.get_profile(request)


@auth_bp.route('/profile', methods=['PUT'])
@authenticate
@validate_request(validate_update_profile)
def update_profile():
    """
    Actualizar perfil del usuario autenticado
    PUT /api/v1/auth/profile
    """
    return auth_controller.update_profile(request)


@auth_bp.route('/change-password', methods=['PUT'])
@authenticate
@validate_request(validate_change_password)
def change_password():
    """
    Cambiar contraseña del usuario autenticado
    PUT /api/v1/auth/change-password
    """
    return auth_controller.change_password(request)


@auth_bp.route('/account', methods=['DELETE'])
@authenticate
def deactivate_account():
    """
    Desactivar cuenta del usuario autenticado
    DELETE /api/v1/auth/account
    """
    return auth_controller.deactivate_account(request)