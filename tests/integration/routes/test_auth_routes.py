"""
Tests de integración para rutas de autenticación
Prueba el flujo HTTP completo: request → middleware → controller → service → DB → response
"""

import pytest
import json

from src.models.user import User


@pytest.mark.integration
class TestAuthRoutes:
    """Tests de integración para endpoints de autenticación"""
    
    # ==================== TESTS DE REGISTER ====================
    
    def test_register_success(self, client, session, sample_register_payload):
        """
        Test: POST /api/v1/auth/register - Registro exitoso
        """
        # Act
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_register_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'token' in data['data']
        assert data['data']['user']['email'] == sample_register_payload['email']
    
    
    def test_register_validation_missing_email(self, client):
        """
        Test: POST /api/v1/auth/register - Falla sin email
        """
        # Arrange
        invalid_payload = {
            'password': 'Password123!',
            'name': 'Test User'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    def test_register_validation_invalid_email(self, client):
        """
        Test: POST /api/v1/auth/register - Falla con email inválido
        """
        # Arrange
        invalid_payload = {
            'email': 'invalid-email',
            'password': 'Password123!',
            'name': 'Test User'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
    
    
    def test_register_validation_weak_password(self, client):
        """
        Test: POST /api/v1/auth/register - Falla con contraseña débil
        """
        # Arrange
        invalid_payload = {
            'email': 'test@example.com',
            'password': '123',  # Contraseña muy débil
            'name': 'Test User'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
    
    
    def test_register_duplicate_email(self, client, session, test_user, sample_register_payload):
        """
        Test: POST /api/v1/auth/register - Falla con email duplicado
        """
        # Arrange - usar email existente
        sample_register_payload['email'] = test_user.email
        
        # Act
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(sample_register_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    # ==================== TESTS DE LOGIN ====================
    
    def test_login_success(self, client, session, test_user, sample_login_payload):
        """
        Test: POST /api/v1/auth/login - Login exitoso
        """
        # Act
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(sample_login_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'token' in data['data']
        assert data['data']['user']['email'] == sample_login_payload['email']
    
    
    def test_login_invalid_credentials(self, client, session, test_user):
        """
        Test: POST /api/v1/auth/login - Falla con credenciales inválidas
        """
        # Arrange
        invalid_payload = {
            'email': test_user.email,
            'password': 'WrongPassword123!'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    def test_login_nonexistent_user(self, client):
        """
        Test: POST /api/v1/auth/login - Falla con usuario inexistente
        """
        # Arrange
        invalid_payload = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    def test_login_inactive_user(self, client, session, inactive_user):
        """
        Test: POST /api/v1/auth/login - Falla con usuario inactivo
        """
        # Arrange
        payload = {
            'email': inactive_user.email,
            'password': 'InactivePassword123!'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'inactivo' in data['message'].lower()
    
    
    def test_login_validation_missing_email(self, client):
        """
        Test: POST /api/v1/auth/login - Falla sin email
        """
        # Arrange
        invalid_payload = {
            'password': 'Password123!'
        }
        
        # Act
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
    
    
    # ==================== TESTS DE GET_PROFILE ====================
    
    def test_get_profile_success(self, client, session, test_user, auth_headers):
        """
        Test: GET /api/v1/auth/profile - Obtener perfil autenticado
        """
        # Act
        response = client.get(
            '/api/v1/auth/profile',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == test_user.id
        assert data['data']['email'] == test_user.email
        assert 'password' not in data['data']
    
    
    def test_get_profile_unauthorized_no_token(self, client):
        """
        Test: GET /api/v1/auth/profile - Falla sin token
        """
        # Act
        response = client.get('/api/v1/auth/profile')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    def test_get_profile_unauthorized_invalid_token(self, client):
        """
        Test: GET /api/v1/auth/profile - Falla con token inválido
        """
        # Arrange
        invalid_headers = {
            'Authorization': 'Bearer invalid-token-12345'
        }
        
        # Act
        response = client.get(
            '/api/v1/auth/profile',
            headers=invalid_headers
        )
        
        # Assert
        assert response.status_code == 401
    
    
    # ==================== TESTS DE UPDATE_PROFILE ====================
    
    def test_update_profile_success(self, client, session, test_user, 
                                    auth_headers, sample_update_profile_payload):
        """
        Test: PUT /api/v1/auth/profile - Actualizar perfil exitosamente
        """
        # Act
        response = client.put(
            '/api/v1/auth/profile',
            data=json.dumps(sample_update_profile_payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == sample_update_profile_payload['name']
    
    
    def test_update_profile_unauthorized(self, client, sample_update_profile_payload):
        """
        Test: PUT /api/v1/auth/profile - Falla sin autenticación
        """
        # Act
        response = client.put(
            '/api/v1/auth/profile',
            data=json.dumps(sample_update_profile_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
    
    
    def test_update_profile_validation_invalid_email(self, client, auth_headers):
        """
        Test: PUT /api/v1/auth/profile - Falla con email inválido
        """
        # Arrange
        invalid_payload = {
            'email': 'invalid-email'
        }
        
        # Act
        response = client.put(
            '/api/v1/auth/profile',
            data=json.dumps(invalid_payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
    
    
    # ==================== TESTS DE CHANGE_PASSWORD ====================
    
    def test_change_password_success(self, client, session, test_user, 
                                     auth_headers, sample_change_password_payload):
        """
        Test: PUT /api/v1/auth/change-password - Cambiar contraseña exitosamente
        """
        # Act
        response = client.put(
            '/api/v1/auth/change-password',
            data=json.dumps(sample_change_password_payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    
    def test_change_password_wrong_current_password(self, client, auth_headers):
        """
        Test: PUT /api/v1/auth/change-password - Falla con contraseña actual incorrecta
        """
        # Arrange
        invalid_payload = {
            'currentPassword': 'WrongPassword123!',
            'newPassword': 'NewPassword456!'
        }
        
        # Act
        response = client.put(
            '/api/v1/auth/change-password',
            data=json.dumps(invalid_payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    
    def test_change_password_unauthorized(self, client, sample_change_password_payload):
        """
        Test: PUT /api/v1/auth/change-password - Falla sin autenticación
        """
        # Act
        response = client.put(
            '/api/v1/auth/change-password',
            data=json.dumps(sample_change_password_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
    
    
    def test_change_password_validation_missing_fields(self, client, auth_headers):
        """
        Test: PUT /api/v1/auth/change-password - Falla sin campos requeridos
        """
        # Arrange
        invalid_payload = {
            'currentPassword': 'TestPassword123!'
            # Falta newPassword
        }
        
        # Act
        response = client.put(
            '/api/v1/auth/change-password',
            data=json.dumps(invalid_payload),
            headers=auth_headers,
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
    
    
    # ==================== TESTS DE DEACTIVATE_ACCOUNT ====================
    
    def test_deactivate_account_success(self, client, session, test_user, auth_headers):
        """
        Test: DELETE /api/v1/auth/account - Desactivar cuenta exitosamente
        """
        # Act
        response = client.delete(
            '/api/v1/auth/account',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verificar que el usuario fue desactivado
        session.refresh(test_user)
        assert test_user.is_active is False
    
    
    def test_deactivate_account_unauthorized(self, client):
        """
        Test: DELETE /api/v1/auth/account - Falla sin autenticación
        """
        # Act
        response = client.delete('/api/v1/auth/account')
        
        # Assert
        assert response.status_code == 401
    
    
    # ==================== TESTS DE FLUJOS COMPLETOS ====================
    
    def test_complete_auth_flow(self, client, session):
        """
        Test: Flujo completo de autenticación
        1. Registrar usuario
        2. Login
        3. Obtener perfil
        4. Actualizar perfil
        5. Cambiar contraseña
        6. Desactivar cuenta
        """
        # 1. Registrar
        register_payload = {
            'email': 'flowtest@example.com',
            'password': 'FlowTest123!',
            'name': 'Flow Test User'
        }
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(register_payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        register_data = json.loads(response.data)
        token = register_data['data']['token']
        
        # 2. Login
        login_payload = {
            'email': register_payload['email'],
            'password': register_payload['password']
        }
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 3. Obtener perfil
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/v1/auth/profile', headers=headers)
        assert response.status_code == 200
        
        # 4. Actualizar perfil
        update_payload = {'name': 'Updated Flow Name'}
        response = client.put(
            '/api/v1/auth/profile',
            data=json.dumps(update_payload),
            headers=headers,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 5. Cambiar contraseña
        change_password_payload = {
            'currentPassword': 'FlowTest123!',
            'newPassword': 'NewFlowPass456!'
        }
        response = client.put(
            '/api/v1/auth/change-password',
            data=json.dumps(change_password_payload),
            headers=headers,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 6. Desactivar cuenta
        response = client.delete('/api/v1/auth/account', headers=headers)
        assert response.status_code == 200
    
    
    def test_rate_limiting_on_login(self, client, session, test_user):
        """
        Test: Rate limiting en endpoint de login
        Verifica que se bloquee después de múltiples intentos
        """
        # Arrange
        payload = {
            'email': test_user.email,
            'password': 'WrongPassword'
        }
        
        # Act - intentar login múltiples veces
        for i in range(5):
            response = client.post(
                '/api/v1/auth/login',
                data=json.dumps(payload),
                content_type='application/json'
            )
        
        # El 6to intento debe estar bloqueado
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'bloqueada' in data['message'].lower()