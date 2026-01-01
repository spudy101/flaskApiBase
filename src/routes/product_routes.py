"""
Product Routes - Flask Blueprint
Equivalente a src/routes/product.routes.js
"""
from flask import Blueprint
from src.controllers.product_controller import product_controller
from src.middlewares.auth_middleware import authenticate
from src.validators.product_validator import validate_create_product, validate_update_product

# Crear blueprint
product_bp = Blueprint('products', __name__, url_prefix='/api/products')


@product_bp.route('', methods=['GET'])
def get_all():
    """GET /api/products - Obtener todos los productos (público)"""
    return product_controller.get_all()


@product_bp.route('/<string:product_id>', methods=['GET'])
def get_by_id(product_id):
    """GET /api/products/:id - Obtener producto por ID (público)"""
    return product_controller.get_by_id(product_id)


@product_bp.route('', methods=['POST'])
@authenticate()
@validate_create_product()
def create():
    """POST /api/products - Crear producto (requiere auth)"""
    return product_controller.create()


@product_bp.route('/<string:product_id>', methods=['PUT'])
@authenticate()
@validate_update_product()
def update(product_id):
    """PUT /api/products/:id - Actualizar producto (requiere auth)"""
    return product_controller.update(product_id)


@product_bp.route('/<string:product_id>', methods=['DELETE'])
@authenticate()
def delete(product_id):
    """DELETE /api/products/:id - Eliminar producto (requiere auth)"""
    return product_controller.delete(product_id)
