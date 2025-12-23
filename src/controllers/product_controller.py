"""
Controller de productos
Equivalente a productController.js
"""

from src.services import product_service
from src.utils import success_response, error_response, paginated_response, logger


class ProductController:
    """Controller de productos"""
    
    def create_product(self, req):
        """
        Crear producto
        POST /api/v1/products
        """
        try:
            user_id = req.user['id']
            product_data = req.get_json()
            
            result = product_service.create_product(product_data, user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Producto creado exitosamente',
                201
            )
            
        except Exception as error:
            logger.error(f'Error en createProduct controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def list_products(self, req):
        """
        Listar productos con filtros y paginación
        GET /api/v1/products
        """
        try:
            filters = {
                'page': req.args.get('page'),
                'limit': req.args.get('limit'),
                'category': req.args.get('category'),
                'isActive': req.args.get('isActive'),
                'minPrice': req.args.get('minPrice'),
                'maxPrice': req.args.get('maxPrice'),
                'search': req.args.get('search'),
                'sortBy': req.args.get('sortBy'),
                'sortOrder': req.args.get('sortOrder')
            }
            
            result = product_service.list_products(filters)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return paginated_response(
                result['data']['products'],
                result['data']['pagination']['page'],
                result['data']['pagination']['limit'],
                result['data']['pagination']['total'],
                'Productos obtenidos exitosamente'
            )
            
        except Exception as error:
            logger.error(f'Error en listProducts controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def get_product_by_id(self, req, product_id):
        """
        Obtener producto por ID
        GET /api/v1/products/:id
        """
        try:
            result = product_service.get_product_by_id(product_id)
            
            if not result['success']:
                return error_response(result['message'], 404)
            
            return success_response(
                result['data'],
                'Producto obtenido exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getProductById controller: {str(error)}')
            
            if str(error) == 'Producto no encontrado':
                return error_response(str(error), 404)
            
            return error_response(str(error), 500)
    
    
    def update_product(self, req, product_id):
        """
        Actualizar producto
        PUT /api/v1/products/:id
        """
        try:
            user_id = req.user['id']
            update_data = req.get_json()
            
            result = product_service.update_product(product_id, update_data, user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Producto actualizado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en updateProduct controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def update_stock(self, req, product_id):
        """
        Actualizar stock del producto
        PATCH /api/v1/products/:id/stock
        """
        try:
            data = req.get_json()
            quantity = data.get('quantity')
            operation = data.get('operation')
            
            result = product_service.update_stock(product_id, quantity, operation)
            
            if not result['success']:
                return error_response(
                    result['message'], 
                    400, 
                    result.get('data')
                )
            
            return success_response(
                result['data'],
                'Stock actualizado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en updateStock controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def delete_product(self, req, product_id):
        """
        Eliminar producto (soft delete)
        DELETE /api/v1/products/:id
        """
        try:
            result = product_service.delete_product(product_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Producto eliminado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en deleteProduct controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def permanently_delete_product(self, req, product_id):
        """
        Eliminar producto permanentemente (Admin)
        DELETE /api/v1/products/:id/permanent
        """
        try:
            result = product_service.permanently_delete_product(product_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Producto eliminado permanentemente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en permanentlyDeleteProduct controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def get_products_by_category(self, req, category):
        """
        Obtener productos por categoría
        GET /api/v1/products/category/:category
        """
        try:
            result = product_service.get_products_by_category(category)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Productos obtenidos exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getProductsByCategory controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def get_product_stats(self, req):
        """
        Obtener estadísticas de productos (Admin)
        GET /api/v1/products/stats
        """
        try:
            result = product_service.get_product_stats()
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Estadísticas obtenidas exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getProductStats controller: {str(error)}')
            return error_response(str(error), 500)


# Exportar instancia única
product_controller = ProductController()