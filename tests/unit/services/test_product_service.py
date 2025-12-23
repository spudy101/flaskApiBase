"""
Tests unitarios para ProductService
Se mockea la base de datos y se testea solo la lógica de negocio
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceUnit:
    """Tests unitarios para ProductService con mocks"""
    
    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.product_service = ProductService()
    
    
    # ==================== TESTS DE CREATE_PRODUCT ====================
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_create_product_success(self, mock_execute_transaction):
        """
        Test: Crear producto exitosamente
        """
        # Arrange
        product_data = {
            'name': 'Test Product',
            'price': 99.99,
            'stock': 50
        }
        user_id = 1
        
        mock_product = {
            'id': 1,
            'name': 'Test Product',
            'price': 99.99,
            'stock': 50,
            'created_by': user_id
        }
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': mock_product
        }
        
        # Act
        result = self.product_service.create_product(product_data, user_id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['name'] == 'Test Product'
        mock_execute_transaction.assert_called_once()
    
    
    # ==================== TESTS DE LIST_PRODUCTS ====================
    
    @patch('src.services.product_service.execute_query')
    def test_list_products_with_pagination(self, mock_execute_query):
        """
        Test: Listar productos con paginación
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'products': [
                    {'id': 1, 'name': 'Product 1'},
                    {'id': 2, 'name': 'Product 2'}
                ],
                'pagination': {
                    'total': 10,
                    'page': 1,
                    'limit': 2,
                    'totalPages': 5
                }
            }
        }
        
        filters = {'page': 1, 'limit': 2}
        
        # Act
        result = self.product_service.list_products(filters)
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['products']) == 2
        assert result['data']['pagination']['total'] == 10
    
    
    @patch('src.services.product_service.execute_query')
    def test_list_products_with_filters(self, mock_execute_query):
        """
        Test: Listar productos con filtros
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'products': [{'id': 1, 'category': 'electronics'}],
                'pagination': {'total': 1, 'page': 1, 'limit': 10, 'totalPages': 1}
            }
        }
        
        filters = {'category': 'electronics', 'minPrice': 50}
        
        # Act
        result = self.product_service.list_products(filters)
        
        # Assert
        assert result['success'] is True
        mock_execute_query.assert_called_once()
    
    
    # ==================== TESTS DE GET_PRODUCT_BY_ID ====================
    
    @patch('src.services.product_service.execute_query')
    def test_get_product_by_id_success(self, mock_execute_query):
        """
        Test: Obtener producto por ID exitosamente
        """
        # Arrange
        product_id = 1
        mock_execute_query.return_value = {
            'success': True,
            'data': {'id': product_id, 'name': 'Test Product'}
        }
        
        # Act
        result = self.product_service.get_product_by_id(product_id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['id'] == product_id
    
    
    @patch('src.services.product_service.execute_query')
    def test_get_product_by_id_not_found(self, mock_execute_query):
        """
        Test: Producto no encontrado
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Producto no encontrado'
        }
        
        # Act
        result = self.product_service.get_product_by_id(999)
        
        # Assert
        assert result['success'] is False
        assert 'no encontrado' in result['message'].lower()
    
    
    # ==================== TESTS DE UPDATE_PRODUCT ====================
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_product_success(self, mock_execute_transaction):
        """
        Test: Actualizar producto exitosamente
        """
        # Arrange
        product_id = 1
        update_data = {'name': 'Updated Name', 'price': 149.99}
        user_id = 1
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'id': product_id, 'name': 'Updated Name', 'price': 149.99}
        }
        
        # Act
        result = self.product_service.update_product(product_id, update_data, user_id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['name'] == 'Updated Name'
    
    
    # ==================== TESTS DE UPDATE_STOCK ====================
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_stock_add_operation(self, mock_execute_transaction):
        """
        Test: Agregar stock exitosamente
        """
        # Arrange
        product_id = 1
        quantity = 10
        operation = 'add'
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {
                'productId': product_id,
                'oldStock': 50,
                'newStock': 60,
                'operation': 'add'
            }
        }
        
        # Act
        result = self.product_service.update_stock(product_id, quantity, operation)
        
        # Assert
        assert result['success'] is True
        assert result['data']['newStock'] == 60
    
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_stock_subtract_operation(self, mock_execute_transaction):
        """
        Test: Restar stock exitosamente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {
                'oldStock': 50,
                'newStock': 40,
                'operation': 'subtract'
            }
        }
        
        # Act
        result = self.product_service.update_stock(1, 10, 'subtract')
        
        # Assert
        assert result['success'] is True
        assert result['data']['newStock'] == 40
    
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_stock_insufficient_stock(self, mock_execute_transaction):
        """
        Test: Falla al intentar restar más stock del disponible
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'Stock insuficiente',
            'data': {'currentStock': 5, 'requested': 10}
        }
        
        # Act
        result = self.product_service.update_stock(1, 10, 'subtract')
        
        # Assert
        assert result['success'] is False
        assert 'insuficiente' in result['message'].lower()
    
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_stock_set_operation(self, mock_execute_transaction):
        """
        Test: Establecer stock a valor específico
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {
                'oldStock': 50,
                'newStock': 100,
                'operation': 'set'
            }
        }
        
        # Act
        result = self.product_service.update_stock(1, 100, 'set')
        
        # Assert
        assert result['success'] is True
        assert result['data']['newStock'] == 100
    
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_update_stock_invalid_operation(self, mock_execute_transaction):
        """
        Test: Falla con operación inválida
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'Operación inválida'
        }
        
        # Act
        result = self.product_service.update_stock(1, 10, 'invalid')
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE DELETE_PRODUCT ====================
    
    @patch('src.services.product_service.execute_with_transaction')
    def test_delete_product_success(self, mock_execute_transaction):
        """
        Test: Eliminar producto (soft delete) exitosamente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'message': 'Producto eliminado exitosamente', 'productId': 1}
        }
        
        # Act
        result = self.product_service.delete_product(1)
        
        # Assert
        assert result['success'] is True
    
    
    # ==================== TESTS DE GET_PRODUCTS_BY_CATEGORY ====================
    
    @patch('src.services.product_service.execute_query')
    def test_get_products_by_category_success(self, mock_execute_query):
        """
        Test: Obtener productos por categoría
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': [
                {'id': 1, 'name': 'Product 1', 'category': 'electronics'},
                {'id': 2, 'name': 'Product 2', 'category': 'electronics'}
            ]
        }
        
        # Act
        result = self.product_service.get_products_by_category('electronics')
        
        # Assert
        assert result['success'] is True
        assert len(result['data']) == 2
    
    
    # ==================== TESTS DE GET_PRODUCT_STATS ====================
    
    @patch('src.services.product_service.execute_query')
    def test_get_product_stats_success(self, mock_execute_query):
        """
        Test: Obtener estadísticas de productos
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'total': 100,
                'active': 80,
                'inactive': 20,
                'outOfStock': 5,
                'lowStock': 10,
                'averagePrice': 75.50,
                'totalStock': 5000
            }
        }
        
        # Act
        result = self.product_service.get_product_stats()
        
        # Assert
        assert result['success'] is True
        assert result['data']['total'] == 100
        assert result['data']['active'] == 80