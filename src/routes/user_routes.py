"""
Rutas de usuarios
Equivalente a userRoutes.js
"""

from flask import Blueprint, request
from src.controllers import user_controller
from src.middlewares import authenticate, authorize, validate_request
from src.validators import (
    validate_uuid_param,
    validate_pagination,
    validate_update_user_role
)

# Crear blueprint
user_bp = Blueprint('users', __name__)

# Todos los endpoints requieren autenticación y rol admin
# En Flask, esto se puede hacer aplicando los decoradores a cada ruta
# o usando before_request del blueprint


@user_bp.before_request
@authenticate
@authorize('admin')
def require_admin():
    """
    Middleware que se ejecuta antes de cada request
    Requiere autenticación y rol admin para todos los endpoints
    """
    pass


@user_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """
    Obtener estadísticas de usuarios
    GET /api/v1/users/stats
    NOTA: Esta ruta debe ir ANTES de /users/:id para evitar conflictos
    """
    return user_controller.get_user_stats(request)


@user_bp.route('/', methods=['GET'])
@validate_request(validate_pagination)
def list_users():
    """
    Listar todos los usuarios con filtros
    GET /api/v1/users
    """
    return user_controller.list_users(request)


@user_bp.route('/<uuid:user_id>', methods=['GET'])
@validate_request(validate_uuid_param)
def get_user_by_id(user_id):
    """
    Obtener usuario por ID
    GET /api/v1/users/:id
    """
    return user_controller.get_user_by_id(request, user_id)


@user_bp.route('/<uuid:user_id>/role', methods=['PUT'])
@validate_request(validate_uuid_param)
@validate_request(validate_update_user_role)
def update_user_role(user_id):
    """
    Actualizar rol de usuario
    PUT /api/v1/users/:id/role
    """
    return user_controller.update_user_role(request, user_id)


@user_bp.route('/<uuid:user_id>/activate', methods=['PUT'])
@validate_request(validate_uuid_param)
def activate_user(user_id):
    """
    Activar usuario
    PUT /api/v1/users/:id/activate
    """
    return user_controller.activate_user(request, user_id)


@user_bp.route('/<uuid:user_id>/deactivate', methods=['PUT'])
@validate_request(validate_uuid_param)
def deactivate_user(user_id):
    """
    Desactivar usuario
    PUT /api/v1/users/:id/deactivate
    """
    return user_controller.deactivate_user(request, user_id)


@user_bp.route('/<uuid:user_id>', methods=['DELETE'])
@validate_request(validate_uuid_param)
def delete_user(user_id):
    """
    Eliminar usuario permanentemente
    DELETE /api/v1/users/:id
    """
    return user_controller.delete_user(request, user_id)