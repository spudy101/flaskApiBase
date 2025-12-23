"""
Tests de integración para rutas de productos
Prueba el flujo HTTP completo con autenticación y autorización
"""

import pytest
import json


@pytest.mark.integration
class TestProductRoutes:
    """Tests de integración para endpoints de productos"""
    
    # ==================== TESTS DE CREATE_PRODUCT ====================
    
    def test_create_product_success_as_admin(self, client, session, admin_user, sample_create_product_payload):
        """
        Test: POST /api/v1/products - Admin puede crear producto
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        
        # Act
        response = client.post(
            '/api/v1/products',
            data=json.dumps(sample_create_product_payload),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == sample_create_product_payload['name']
    
    
    def test_create_product_forbidden_as_user(self, client, auth_headers, sample_create_product_payload):
        """
        Test: POST /api/v1/products - Usuario normal no puede crear producto
        """
        # Act
        response = client.post(
            '/api/v1/products',
            data=json.dumps(sample_create_product_payload),
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    def test_create_product_unauthorized_without_token(self, client, sample_create_product_payload):
        """
        Test: POST /api/v1/products - Falla sin token
        """
        # Act
        response = client.post(
            '/api/v1/products',
            data=json.dumps(sample_create_product_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
    
    
    # ==================== TESTS DE LIST_PRODUCTS ====================
    
    def test_list_products_success(self, client, session, create_product):
        """
        Test: GET /api/v1/products - Listar productos (público)
        """
        # Arrange
        create_product(name='Product 1')
        create_product(name='Product 2')
        
        # Act
        response = client.get('/api/v1/products')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'products' in data['data']
        assert 'pagination' in data['data']
    
    
    def test_list_products_with_pagination(self, client, create_product):
        """
        Test: GET /api/v1/products - Paginación funciona correctamente
        """
        # Arrange
        for i in range(5):
            create_product(name=f'Product {i}')
        
        # Act
        response = client.get('/api/v1/products?page=1&limit=3')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['products']) <= 3
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['limit'] == 3
    
    
    def test_list_products_filter_by_category(self, client, create_product):
        """
        Test: GET /api/v1/products - Filtrar por categoría
        """
        # Arrange
        create_product(name='Electronics', category='electronics')
        create_product(name='Clothing', category='clothing')
        
        # Act
        response = client.get('/api/v1/products?category=electronics')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        for product in data['data']['products']:
            assert product['category'] == 'electronics'
    
    
    # ==================== TESTS DE GET_PRODUCT_BY_ID ====================
    
    def test_get_product_by_id_success(self, client, test_product):
        """
        Test: GET /api/v1/products/:id - Obtener producto por ID
        """
        # Act
        response = client.get(f'/api/v1/products/{test_product.id}')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == str(test_product.id)
    
    
    def test_get_product_by_id_not_found(self, client):
        """
        Test: GET /api/v1/products/:id - Producto inexistente
        """
        # Act
        from uuid import uuid4
        response = client.get(f'/api/v1/products/{uuid4()}')
        
        # Assert
        assert response.status_code == 404
    
    
    # ==================== TESTS DE UPDATE_PRODUCT ====================
    
    def test_update_product_success_as_admin(self, client, session, test_product, admin_user):
        """
        Test: PUT /api/v1/products/:id - Admin puede actualizar
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        update_data = {'name': 'Updated Product Name'}
        
        # Act
        response = client.put(
            f'/api/v1/products/{test_product.id}',
            data=json.dumps(update_data),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Product Name'
    
    
    def test_update_product_forbidden_as_user(self, client, test_product, auth_headers):
        """
        Test: PUT /api/v1/products/:id - Usuario normal no puede actualizar
        """
        # Arrange
        update_data = {'name': 'Trying to Update'}
        
        # Act
        response = client.put(
            f'/api/v1/products/{test_product.id}',
            data=json.dumps(update_data),
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE UPDATE_STOCK ====================
    
    def test_update_stock_add_success(self, client, session, test_product, admin_user):
        """
        Test: PATCH /api/v1/products/:id/stock - Agregar stock
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        payload = {'quantity': 20, 'operation': 'add'}
        
        # Act
        response = client.patch(
            f'/api/v1/products/{test_product.id}/stock',
            data=json.dumps(payload),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_update_stock_subtract_success(self, client, test_product, admin_user):
        """
        Test: PATCH /api/v1/products/:id/stock - Restar stock
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        payload = {'quantity': 10, 'operation': 'subtract'}
        
        # Act
        response = client.patch(
            f'/api/v1/products/{test_product.id}/stock',
            data=json.dumps(payload),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
    
    
    def test_update_stock_insufficient_stock(self, client, test_product, admin_user):
        """
        Test: PATCH /api/v1/products/:id/stock - Falla con stock insuficiente
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        payload = {'quantity': 999999, 'operation': 'subtract'}
        
        # Act
        response = client.patch(
            f'/api/v1/products/{test_product.id}/stock',
            data=json.dumps(payload),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 400
    
    
    # ==================== TESTS DE DELETE_PRODUCT ====================
    
    def test_delete_product_success_as_admin(self, client, session, test_product, admin_user):
        """
        Test: DELETE /api/v1/products/:id - Admin puede eliminar (soft delete)
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.delete(
            f'/api/v1/products/{test_product.id}',
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_delete_product_forbidden_as_user(self, client, test_product, auth_headers):
        """
        Test: DELETE /api/v1/products/:id - Usuario normal no puede eliminar
        """
        # Act
        response = client.delete(
            f'/api/v1/products/{test_product.id}',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE GET_PRODUCTS_BY_CATEGORY ====================
    
    def test_get_products_by_category_success(self, client, create_product):
        """
        Test: GET /api/v1/products/category/:category
        """
        # Arrange
        create_product(name='Electronics 1', category='electronics')
        create_product(name='Electronics 2', category='electronics')
        
        # Act
        response = client.get('/api/v1/products/category/electronics')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert all(p['category'] == 'electronics' for p in data['data'])
    
    
    # ==================== TESTS DE GET_PRODUCT_STATS ====================
    
    def test_get_product_stats_success_as_admin(self, client, admin_user):
        """
        Test: GET /api/v1/products/stats - Admin puede ver estadísticas
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.get('/api/v1/products/stats', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total' in data['data']
    
    
    def test_get_product_stats_forbidden_as_user(self, client, auth_headers):
        """
        Test: GET /api/v1/products/stats - Usuario normal no puede ver estadísticas
        """
        # Act
        response = client.get('/api/v1/products/stats', headers=auth_headers)
        
        # Assert
        assert response.status_code == 403