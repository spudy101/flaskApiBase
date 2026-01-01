"""
Product Controller
Equivalente a src/controllers/product.controller.js
"""
from flask import request, g
from src.repositories.product_repository import product_repository
from src.dto.product_dto import CreateProductDTO, UpdateProductDTO, ProductResponseDTO
from src.utils.response_util import ApiResponse
from src.utils.app_error import AppError


class ProductController:
    """Product controller"""
    
    def get_all(self):
        """GET /api/products - Obtiene todos los productos"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            category = request.args.get('category')
            
            # Filtros
            filters = {'is_active': True}
            if category:
                filters['category'] = category
            
            result = product_repository.find_with_pagination(page=page, limit=limit, **filters)
            
            products_dto = [ProductResponseDTO.from_model(p).to_dict() for p in result['rows']]
            
            response_data = {
                'products': products_dto,
                'pagination': {
                    'page': result['page'],
                    'limit': result['limit'],
                    'total': result['count'],
                    'total_pages': result['total_pages']
                }
            }
            
            return ApiResponse.success('Productos obtenidos', response_data)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def get_by_id(self, product_id: str):
        """GET /api/products/:id"""
        try:
            product = product_repository.find_by_id(product_id)
            
            if not product:
                return ApiResponse.not_found('Producto no encontrado')
            
            product_dto = ProductResponseDTO.from_model(product, include_creator=True).to_dict()
            
            return ApiResponse.success('Producto obtenido', product_dto)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def create(self):
        """POST /api/products - Crea un producto"""
        try:
            data = request.get_json()
            user = g.user
            
            dto = CreateProductDTO.from_request(data, user['id'])
            
            product = product_repository.create(dto.to_dict())
            product_dto = ProductResponseDTO.from_model(product).to_dict()
            
            return ApiResponse.created('Producto creado', product_dto)
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def update(self, product_id: str):
        """PUT /api/products/:id"""
        try:
            user = g.user
            product = product_repository.find_by_id(product_id)
            
            if not product:
                return ApiResponse.not_found('Producto no encontrado')
            
            # Solo el creador o admin puede actualizar
            if product.created_by != user['id'] and user['role'] != 'admin':
                return ApiResponse.forbidden('No tienes permisos para actualizar este producto')
            
            data = request.get_json()
            dto = UpdateProductDTO.from_request(data)
            
            updated_product = product_repository.update(product_id, dto.to_dict())
            product_dto = ProductResponseDTO.from_model(updated_product).to_dict()
            
            return ApiResponse.success('Producto actualizado', product_dto)
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def delete(self, product_id: str):
        """DELETE /api/products/:id"""
        try:
            user = g.user
            product = product_repository.find_by_id(product_id)
            
            if not product:
                return ApiResponse.not_found('Producto no encontrado')
            
            # Solo el creador o admin puede eliminar
            if product.created_by != user['id'] and user['role'] != 'admin':
                return ApiResponse.forbidden('No tienes permisos para eliminar este producto')
            
            # Soft delete
            product_repository.soft_delete(product_id)
            
            return ApiResponse.success('Producto eliminado')
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))


# Singleton instance
product_controller = ProductController()
