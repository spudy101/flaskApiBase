"""
User Routes - Flask Blueprint
Equivalente a src/routes/user.routes.js
"""
from flask import Blueprint
from src.controllers.user_controller import user_controller
from src.middlewares.auth_middleware import authenticate, authorize

# Crear blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('', methods=['GET'])
@authenticate()
def get_all():
    """GET /api/users - Obtener todos los usuarios"""
    return user_controller.get_all()


@user_bp.route('/<string:user_id>', methods=['GET'])
@authenticate()
def get_by_id(user_id):
    """GET /api/users/:id - Obtener usuario por ID"""
    return user_controller.get_by_id(user_id)


@user_bp.route('/<string:user_id>', methods=['PUT'])
@authenticate()
def update(user_id):
    """PUT /api/users/:id - Actualizar usuario"""
    return user_controller.update(user_id)


@user_bp.route('/<string:user_id>', methods=['DELETE'])
@authenticate()
@authorize(['admin'])
def delete(user_id):
    """DELETE /api/users/:id - Eliminar usuario (solo admin)"""
    return user_controller.delete(user_id)
