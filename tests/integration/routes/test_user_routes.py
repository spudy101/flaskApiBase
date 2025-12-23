"""
Tests de integración para rutas de usuarios
Prueba el flujo HTTP completo con autenticación y autorización de admin
"""

import pytest
import json


@pytest.mark.integration
class TestUserRoutes:
    """Tests de integración para endpoints de usuarios (solo admin)"""
    
    # ==================== TESTS DE LIST_USERS ====================
    
    def test_list_users_success_as_admin(self, client, session, admin_user, create_user):
        """
        Test: GET /api/v1/users - Admin puede listar usuarios
        """
        # Arrange
        create_user(email='user1@example.com')
        create_user(email='user2@example.com')
        
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.get('/api/v1/users', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'users' in data['data']
        assert 'pagination' in data['data']
    
    
    def test_list_users_forbidden_as_regular_user(self, client, auth_headers):
        """
        Test: GET /api/v1/users - Usuario normal no puede listar
        """
        # Act
        response = client.get('/api/v1/users', headers=auth_headers)
        
        # Assert
        assert response.status_code == 403
    
    
    def test_list_users_unauthorized_without_token(self, client):
        """
        Test: GET /api/v1/users - Falla sin token
        """
        # Act
        response = client.get('/api/v1/users')
        
        # Assert
        assert response.status_code == 401
    
    
    def test_list_users_with_pagination(self, client, admin_user, create_user):
        """
        Test: GET /api/v1/users - Paginación funciona
        """
        # Arrange
        for i in range(5):
            create_user(email=f'user{i}@example.com')
        
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.get('/api/v1/users?page=1&limit=3', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['users']) <= 3
    
    
    def test_list_users_filter_by_role(self, client, admin_user, create_user):
        """
        Test: GET /api/v1/users - Filtrar por rol
        """
        # Arrange
        create_user(email='admin2@example.com', role='admin')
        create_user(email='user1@example.com', role='user')
        
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.get('/api/v1/users?role=admin', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        for user in data['data']['users']:
            assert user['role'] == 'admin'
    
    
    # ==================== TESTS DE GET_USER_BY_ID ====================
    
    def test_get_user_by_id_success_as_admin(self, client, test_user, admin_user):
        """
        Test: GET /api/v1/users/:id - Admin puede obtener usuario
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
        response = client.get(f'/api/v1/users/{test_user.id}', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == str(test_user.id)
    
    
    def test_get_user_by_id_forbidden_as_regular_user(self, client, test_user, auth_headers):
        """
        Test: GET /api/v1/users/:id - Usuario normal no puede obtener
        """
        # Act
        response = client.get(f'/api/v1/users/{test_user.id}', headers=auth_headers)
        
        # Assert
        assert response.status_code == 403
    
    
    def test_get_user_by_id_not_found(self, client, admin_user):
        """
        Test: GET /api/v1/users/:id - Usuario inexistente
        """
        # Arrange
        from src.utils import generate_token
        from uuid import uuid4
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Act
        response = client.get(f'/api/v1/users/{uuid4()}', headers=headers)
        
        # Assert
        assert response.status_code == 404
    
    
    # ==================== TESTS DE UPDATE_USER_ROLE ====================
    
    def test_update_user_role_success_as_admin(self, client, session, test_user, admin_user):
        """
        Test: PUT /api/v1/users/:id/role - Admin puede actualizar rol
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        payload = {'role': 'admin'}
        
        # Act
        response = client.put(
            f'/api/v1/users/{test_user.id}/role',
            data=json.dumps(payload),
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['role'] == 'admin'
    
    
    def test_update_user_role_forbidden_as_regular_user(self, client, test_user, auth_headers):
        """
        Test: PUT /api/v1/users/:id/role - Usuario normal no puede actualizar rol
        """
        # Arrange
        payload = {'role': 'admin'}
        
        # Act
        response = client.put(
            f'/api/v1/users/{test_user.id}/role',
            data=json.dumps(payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE ACTIVATE_USER ====================
    
    def test_activate_user_success_as_admin(self, client, session, inactive_user, admin_user):
        """
        Test: PUT /api/v1/users/:id/activate - Admin puede activar usuario
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
        response = client.put(
            f'/api/v1/users/{inactive_user.id}/activate',
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_activate_user_forbidden_as_regular_user(self, client, inactive_user, auth_headers):
        """
        Test: PUT /api/v1/users/:id/activate - Usuario normal no puede activar
        """
        # Act
        response = client.put(
            f'/api/v1/users/{inactive_user.id}/activate',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE DEACTIVATE_USER ====================
    
    def test_deactivate_user_success_as_admin(self, client, session, test_user, admin_user):
        """
        Test: PUT /api/v1/users/:id/deactivate - Admin puede desactivar usuario
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
        response = client.put(
            f'/api/v1/users/{test_user.id}/deactivate',
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_deactivate_user_forbidden_as_regular_user(self, client, test_user, auth_headers):
        """
        Test: PUT /api/v1/users/:id/deactivate - Usuario normal no puede desactivar
        """
        # Act
        response = client.put(
            f'/api/v1/users/{test_user.id}/deactivate',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE DELETE_USER ====================
    
    def test_delete_user_success_as_admin(self, client, session, test_user, admin_user):
        """
        Test: DELETE /api/v1/users/:id - Admin puede eliminar usuario
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
            f'/api/v1/users/{test_user.id}',
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_delete_user_forbidden_as_regular_user(self, client, test_user, auth_headers):
        """
        Test: DELETE /api/v1/users/:id - Usuario normal no puede eliminar
        """
        # Act
        response = client.delete(
            f'/api/v1/users/{test_user.id}',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE GET_USER_STATS ====================
    
    def test_get_user_stats_success_as_admin(self, client, admin_user):
        """
        Test: GET /api/v1/users/stats - Admin puede ver estadísticas
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
        response = client.get('/api/v1/users/stats', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total' in data['data']
        assert 'active' in data['data']
        assert 'admins' in data['data']
    
    
    def test_get_user_stats_forbidden_as_regular_user(self, client, auth_headers):
        """
        Test: GET /api/v1/users/stats - Usuario normal no puede ver estadísticas
        """
        # Act
        response = client.get('/api/v1/users/stats', headers=auth_headers)
        
        # Assert
        assert response.status_code == 403
    
    
    # ==================== TESTS DE FLUJO COMPLETO ====================
    
    def test_complete_admin_user_management_flow(self, client, session, create_user, admin_user):
        """
        Test: Flujo completo de gestión de usuarios por admin
        1. Crear usuario (mediante auth)
        2. Listar usuarios
        3. Obtener usuario específico
        4. Actualizar rol
        5. Desactivar
        6. Activar
        7. Eliminar
        """
        # Arrange
        from src.utils import generate_token
        admin_token = generate_token({
            'id': admin_user.id,
            'email': admin_user.email,
            'role': admin_user.role
        })
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        
        # 1. Crear usuario (usando create_user fixture)
        new_user = create_user(email='testflow@example.com', role='user')
        
        # 2. Listar usuarios
        response = client.get('/api/v1/users', headers=headers)
        assert response.status_code == 200
        
        # 3. Obtener usuario específico
        response = client.get(f'/api/v1/users/{new_user.id}', headers=headers)
        assert response.status_code == 200
        
        # 4. Actualizar rol
        response = client.put(
            f'/api/v1/users/{new_user.id}/role',
            data=json.dumps({'role': 'admin'}),
            headers=headers
        )
        assert response.status_code == 200
        
        # 5. Desactivar
        response = client.put(
            f'/api/v1/users/{new_user.id}/deactivate',
            headers=headers
        )
        assert response.status_code == 200
        
        # 6. Activar
        response = client.put(
            f'/api/v1/users/{new_user.id}/activate',
            headers=headers
        )
        assert response.status_code == 200
        
        # 7. Eliminar
        response = client.delete(
            f'/api/v1/users/{new_user.id}',
            headers=headers
        )
        assert response.status_code == 200