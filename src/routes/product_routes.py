"""
Rutas de productos
Equivalente a productRoutes.js
"""

from flask import Blueprint, request
from src.controllers import product_controller
from src.middlewares import (
    authenticate,
    authorize,
    optional_auth,
    request_lock,
    validate_request
)
from src.validators import (
    validate_create_product,
    validate_update_product,
    validate_get_product_by_id,
    validate_delete_product,
    validate_list_products,
    validate_update_stock
)

# Crear blueprint
product_bp = Blueprint('products', __name__)


@product_bp.route('/stats', methods=['GET'])
@authenticate
@authorize('admin')
def get_product_stats():
    """
    Obtener estadísticas de productos
    GET /api/v1/products/stats
    NOTA: Esta ruta debe ir ANTES de /products/:id para evitar conflictos
    """
    return product_controller.get_product_stats(request)


@product_bp.route('/category/<string:category>', methods=['GET'])
def get_products_by_category(category):
    """
    Obtener productos por categoría
    GET /api/v1/products/category/:category
    NOTA: Esta ruta debe ir ANTES de /products/:id para evitar conflictos
    """
    return product_controller.get_products_by_category(request, category)


@product_bp.route('/', methods=['GET'])
@optional_auth
@validate_request(validate_list_products)
def list_products():
    """
    Listar productos con filtros y paginación
    GET /api/v1/products
    """
    return product_controller.list_products(request)


@product_bp.route('/<uuid:product_id>', methods=['GET'])
@validate_request(validate_get_product_by_id)
def get_product_by_id(product_id):
    """
    Obtener producto por ID
    GET /api/v1/products/:id
    """
    return product_controller.get_product_by_id(request, product_id)


@product_bp.route('/', methods=['POST'])
@authenticate
@authorize('admin')
@request_lock()
@validate_request(validate_create_product)
def create_product():
    """
    Crear producto
    POST /api/v1/products
    """
    return product_controller.create_product(request)


@product_bp.route('/<uuid:product_id>', methods=['PUT'])
@authenticate
@authorize('admin')
@request_lock()
@validate_request(validate_update_product)
def update_product(product_id):
    """
    Actualizar producto
    PUT /api/v1/products/:id
    """
    return product_controller.update_product(request, product_id)


@product_bp.route('/<uuid:product_id>/stock', methods=['PATCH'])
@authenticate
@authorize('admin')
@request_lock(timeout=10000)  # 10 segundos para operaciones de stock
@validate_request(validate_update_stock)
def update_stock(product_id):
    """
    Actualizar stock del producto
    PATCH /api/v1/products/:id/stock
    """
    return product_controller.update_stock(request, product_id)


@product_bp.route('/<uuid:product_id>', methods=['DELETE'])
@authenticate
@authorize('admin')
@request_lock()
@validate_request(validate_delete_product)
def delete_product(product_id):
    """
    Eliminar producto (soft delete)
    DELETE /api/v1/products/:id
    """
    return product_controller.delete_product(request, product_id)


@product_bp.route('/<uuid:product_id>/permanent', methods=['DELETE'])
@authenticate
@authorize('admin')
@validate_request(validate_delete_product)
def permanently_delete_product(product_id):
    """
    Eliminar producto permanentemente
    DELETE /api/v1/products/:id/permanent
    """
    return product_controller.permanently_delete_product(request, product_id)