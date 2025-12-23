"""
Tests de integración para ProductService
Se usa base de datos real (SQLite en memoria) para verificar queries y transacciones
"""

import pytest
from src.services.product_service import ProductService
from src.models.product import Product


@pytest.mark.integration
class TestProductServiceIntegration:
    """Tests de integración para ProductService con DB real"""
    
    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.product_service = ProductService()
    
    
    # ==================== TESTS DE CREATE_PRODUCT ====================
    
    def test_create_product_persists_in_database(self, session, test_user, sample_create_product_payload):
        """
        Test: Crear producto persiste en la base de datos
        """
        # Act
        result = self.product_service.create_product(sample_create_product_payload, test_user.id)
        
        # Assert
        assert result['success'] is True
        product = session.query(Product).filter_by(name=sample_create_product_payload['name']).first()
        assert product is not None
        assert product.name == sample_create_product_payload['name']
        assert product.price == sample_create_product_payload['price']
        assert product.created_by == test_user.id
    
    
    # ==================== TESTS DE LIST_PRODUCTS ====================
    
    def test_list_products_returns_paginated_results(self, session, create_product):
        """
        Test: Listar productos retorna resultados paginados
        """
        # Arrange - crear varios productos
        for i in range(5):
            create_product(name=f'Product {i}', price=10.0 * i)
        
        # Act
        result = self.product_service.list_products({'page': 1, 'limit': 3})
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['products']) == 3
        assert result['data']['pagination']['total'] >= 5
        assert result['data']['pagination']['totalPages'] >= 2
    
    
    def test_list_products_filter_by_category(self, session, create_product):
        """
        Test: Filtrar productos por categoría
        """
        # Arrange
        create_product(name='Electronics 1', category='electronics')
        create_product(name='Electronics 2', category='electronics')
        create_product(name='Clothing 1', category='clothing')
        
        # Act
        result = self.product_service.list_products({'category': 'electronics'})
        
        # Assert
        assert result['success'] is True
        assert all(p['category'] == 'electronics' for p in result['data']['products'])
    
    
    def test_list_products_filter_by_price_range(self, session, create_product):
        """
        Test: Filtrar productos por rango de precio
        """
        # Arrange
        create_product(name='Cheap', price=10.0)
        create_product(name='Medium', price=50.0)
        create_product(name='Expensive', price=100.0)
        
        # Act
        result = self.product_service.list_products({'minPrice': 30, 'maxPrice': 70})
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['products']) >= 1
        for product in result['data']['products']:
            assert 30 <= product['price'] <= 70
    
    
    def test_list_products_search_by_name(self, session, create_product):
        """
        Test: Buscar productos por nombre
        """
        # Arrange
        create_product(name='Laptop Dell')
        create_product(name='Laptop HP')
        create_product(name='Mouse Logitech')
        
        # Act
        result = self.product_service.list_products({'search': 'Laptop'})
        
        # Assert
        assert result['success'] is True
        assert all('Laptop' in p['name'] for p in result['data']['products'])
    
    
    def test_list_products_filter_by_active_status(self, session, create_product):
        """
        Test: Filtrar productos por estado activo
        """
        # Arrange
        create_product(name='Active', is_active=True)
        create_product(name='Inactive', is_active=False)
        
        # Act
        result = self.product_service.list_products({'isActive': 'true'})
        
        # Assert
        assert result['success'] is True
        assert all(p['is_active'] is True for p in result['data']['products'])
    
    
    # ==================== TESTS DE GET_PRODUCT_BY_ID ====================
    
    def test_get_product_by_id_returns_product(self, session, test_product):
        """
        Test: Obtener producto por ID retorna datos correctos
        """
        # Act
        result = self.product_service.get_product_by_id(test_product.id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['id'] == test_product.id
        assert result['data']['name'] == test_product.name
    
    
    def test_get_product_by_id_not_found(self, session):
        """
        Test: Obtener producto inexistente falla
        """
        # Act
        result = self.product_service.get_product_by_id(99999)
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE UPDATE_PRODUCT ====================
    
    def test_update_product_modifies_database(self, session, test_product, test_user):
        """
        Test: Actualizar producto modifica la base de datos
        """
        # Arrange
        update_data = {'name': 'Updated Name', 'price': 199.99}
        
        # Act
        result = self.product_service.update_product(test_product.id, update_data, test_user.id)
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.name == 'Updated Name'
        assert test_product.price == 199.99
    
    
    def test_update_product_partial_update(self, session, test_product, test_user):
        """
        Test: Actualización parcial solo modifica campos especificados
        """
        # Arrange
        original_price = test_product.price
        update_data = {'name': 'New Name Only'}
        
        # Act
        result = self.product_service.update_product(test_product.id, update_data, test_user.id)
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.name == 'New Name Only'
        assert test_product.price == original_price  # No cambió
    
    
    # ==================== TESTS DE UPDATE_STOCK ====================
    
    def test_update_stock_add_increases_stock(self, session, test_product):
        """
        Test: Operación 'add' incrementa el stock
        """
        # Arrange
        original_stock = test_product.stock
        
        # Act
        result = self.product_service.update_stock(test_product.id, 20, 'add')
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.stock == original_stock + 20
    
    
    def test_update_stock_subtract_decreases_stock(self, session, test_product):
        """
        Test: Operación 'subtract' disminuye el stock
        """
        # Arrange
        original_stock = test_product.stock
        
        # Act
        result = self.product_service.update_stock(test_product.id, 10, 'subtract')
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.stock == original_stock - 10
    
    
    def test_update_stock_subtract_fails_with_insufficient_stock(self, session, test_product):
        """
        Test: No se puede restar más stock del disponible
        """
        # Arrange
        quantity_to_subtract = test_product.stock + 50
        
        # Act
        result = self.product_service.update_stock(test_product.id, quantity_to_subtract, 'subtract')
        
        # Assert
        assert result['success'] is False
        assert 'insuficiente' in result['message'].lower()
    
    
    def test_update_stock_set_changes_to_specific_value(self, session, test_product):
        """
        Test: Operación 'set' establece stock a valor específico
        """
        # Act
        result = self.product_service.update_stock(test_product.id, 75, 'set')
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.stock == 75
    
    
    def test_update_stock_set_rejects_negative_value(self, session, test_product):
        """
        Test: No se puede establecer stock negativo
        """
        # Act
        result = self.product_service.update_stock(test_product.id, -10, 'set')
        
        # Assert
        assert result['success'] is False
    
    
    def test_update_stock_with_lock_prevents_race_conditions(self, session, test_product):
        """
        Test: Update con lock evita condiciones de carrera
        Nota: Test conceptual - en ambiente real necesitaría concurrencia
        """
        # Arrange
        original_stock = test_product.stock
        
        # Act - múltiples operaciones secuenciales
        result1 = self.product_service.update_stock(test_product.id, 5, 'subtract')
        result2 = self.product_service.update_stock(test_product.id, 3, 'subtract')
        
        # Assert
        assert result1['success'] is True
        assert result2['success'] is True
        session.refresh(test_product)
        assert test_product.stock == original_stock - 8
    
    
    # ==================== TESTS DE DELETE_PRODUCT ====================
    
    def test_delete_product_soft_delete(self, session, test_product):
        """
        Test: Delete marca producto como inactivo (soft delete)
        """
        # Act
        result = self.product_service.delete_product(test_product.id)
        
        # Assert
        assert result['success'] is True
        session.refresh(test_product)
        assert test_product.is_active is False
        # El producto aún existe en DB
        assert session.query(Product).get(test_product.id) is not None
    
    
    def test_permanently_delete_product_hard_delete(self, session, test_product):
        """
        Test: Permanently delete elimina producto de la base de datos
        """
        # Arrange
        product_id = test_product.id
        
        # Act
        result = self.product_service.permanently_delete_product(product_id)
        
        # Assert
        assert result['success'] is True
        # El producto ya no existe en DB
        assert session.query(Product).get(product_id) is None
    
    
    # ==================== TESTS DE GET_PRODUCTS_BY_CATEGORY ====================
    
    def test_get_products_by_category_returns_filtered_results(self, session, create_product):
        """
        Test: Obtener productos por categoría retorna solo esa categoría
        """
        # Arrange
        create_product(name='Electronics 1', category='electronics')
        create_product(name='Electronics 2', category='electronics')
        create_product(name='Clothing', category='clothing')
        
        # Act
        result = self.product_service.get_products_by_category('electronics')
        
        # Assert
        assert result['success'] is True
        assert len(result['data']) >= 2
        assert all(p['category'] == 'electronics' for p in result['data'])
    
    
    def test_get_products_by_category_only_active_products(self, session, create_product):
        """
        Test: Solo retorna productos activos de la categoría
        """
        # Arrange
        create_product(name='Active Electronics', category='electronics', is_active=True)
        create_product(name='Inactive Electronics', category='electronics', is_active=False)
        
        # Act
        result = self.product_service.get_products_by_category('electronics')
        
        # Assert
        assert result['success'] is True
        assert all(p['is_active'] is True for p in result['data'])
    
    
    # ==================== TESTS DE GET_PRODUCT_STATS ====================
    
    def test_get_product_stats_calculates_correctly(self, session, create_product):
        """
        Test: Estadísticas de productos se calculan correctamente
        """
        # Arrange
        create_product(name='Active 1', price=50.0, stock=100, is_active=True)
        create_product(name='Active 2', price=100.0, stock=0, is_active=True)
        create_product(name='Inactive', price=75.0, stock=50, is_active=False)
        
        # Act
        result = self.product_service.get_product_stats()
        
        # Assert
        assert result['success'] is True
        stats = result['data']
        assert stats['total'] >= 3
        assert stats['active'] >= 2
        assert stats['inactive'] >= 1
        assert stats['outOfStock'] >= 1
        assert stats['averagePrice'] > 0