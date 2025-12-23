"""
Tests unitarios para AuthService
Se mockea la base de datos y se testea solo la lógica de negocio
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.auth_service import AuthService


@pytest.mark.unit
class TestAuthServiceUnit:
    """Tests unitarios para AuthService con mocks"""
    
    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.auth_service = AuthService()
    
    
    # ==================== TESTS DE REGISTER ====================
    
    @patch('src.services.auth_service.execute_with_transaction')
    @patch('src.services.auth_service.generate_token')
    def test_register_success(self, mock_generate_token, mock_execute_transaction, sample_user_data):
        """
        Test: Registro exitoso de usuario
        Verifica que se retorne el usuario y token correctamente
        """
        # Arrange
        mock_token = 'mock-jwt-token-12345'
        mock_generate_token.return_value = mock_token
        
        mock_user_dict = {
            'id': 1,
            'email': sample_user_data['email'],
            'name': sample_user_data['name'],
            'role': sample_user_data['role'],
            'is_active': True
        }
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {
                'user': mock_user_dict,
                'token': mock_token
            }
        }
        
        # Act
        result = self.auth_service.register(sample_user_data)
        
        # Assert
        assert result['success'] is True
        assert result['data']['user']['email'] == sample_user_data['email']
        assert result['data']['token'] == mock_token
        mock_execute_transaction.assert_called_once()
    
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_register_duplicate_email(self, mock_execute_transaction, sample_user_data):
        """
        Test: Intento de registro con email duplicado
        Verifica que se maneje el error apropiadamente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'El email ya está registrado',
            'data': None
        }
        
        # Act
        result = self.auth_service.register(sample_user_data)
        
        # Assert
        assert result['success'] is False
        assert 'email' in result['message'].lower()
    
    
    # ==================== TESTS DE LOGIN ====================
    
    @patch('src.services.auth_service.execute_query')
    @patch('src.services.auth_service.generate_token')
    @patch('src.services.auth_service.User')
    @patch('src.services.auth_service.LoginAttempt')
    def test_login_success(self, mock_login_attempt_class, mock_user_class, 
                          mock_generate_token, mock_execute_query, 
                          mock_user, sample_login_data):
        """
        Test: Login exitoso
        Verifica que se retorne usuario y token
        """
        # Arrange
        mock_token = 'mock-jwt-token-67890'
        mock_generate_token.return_value = mock_token
        
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'user': mock_user.to_dict(),
                'token': mock_token
            }
        }
        
        # Act
        result = self.auth_service.login(
            sample_login_data['email'],
            sample_login_data['password']
        )
        
        # Assert
        assert result['success'] is True
        assert 'user' in result['data']
        assert 'token' in result['data']
        assert result['data']['token'] == mock_token
    
    
    @patch('src.services.auth_service.execute_query')
    def test_login_invalid_credentials(self, mock_execute_query, sample_login_data):
        """
        Test: Login con credenciales inválidas
        Verifica que se retorne error apropiado
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Credenciales inválidas',
            'data': None
        }
        
        # Act
        result = self.auth_service.login(
            sample_login_data['email'],
            'wrong-password'
        )
        
        # Assert
        assert result['success'] is False
        assert 'credenciales' in result['message'].lower()
    
    
    @patch('src.services.auth_service.execute_query')
    def test_login_inactive_user(self, mock_execute_query, sample_login_data):
        """
        Test: Login con usuario inactivo
        Verifica que se rechace el login
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Usuario inactivo',
            'data': None
        }
        
        # Act
        result = self.auth_service.login(
            sample_login_data['email'],
            sample_login_data['password']
        )
        
        # Assert
        assert result['success'] is False
        assert 'inactivo' in result['message'].lower()
    
    
    @patch('src.services.auth_service.execute_query')
    def test_login_account_blocked(self, mock_execute_query, sample_login_data):
        """
        Test: Login con cuenta bloqueada temporalmente
        Verifica que se informe del bloqueo
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Cuenta bloqueada temporalmente. Intenta nuevamente en 15 minutos.',
            'data': None
        }
        
        # Act
        result = self.auth_service.login(
            sample_login_data['email'],
            sample_login_data['password']
        )
        
        # Assert
        assert result['success'] is False
        assert 'bloqueada' in result['message'].lower()
    
    
    # ==================== TESTS DE HANDLE_FAILED_ATTEMPT ====================
    
    @patch('src.services.auth_service.db')
    def test_handle_failed_attempt_first_attempt(self, mock_db, mock_login_attempt):
        """
        Test: Primer intento fallido
        Verifica que se cree un registro con attempts=1
        """
        # Arrange
        email = 'test@example.com'
        login_attempt = False  # No existe aún
        
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        
        # Act
        self.auth_service.handle_failed_attempt(email, login_attempt)
        
        # Assert
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    
    @patch('src.services.auth_service.db')
    def test_handle_failed_attempt_increment(self, mock_db, mock_login_attempt):
        """
        Test: Incrementar intentos fallidos
        Verifica que se incremente el contador
        """
        # Arrange
        email = 'test@example.com'
        mock_login_attempt.attempts = 2
        mock_login_attempt.blocked_until = None
        
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        
        # Act
        self.auth_service.handle_failed_attempt(email, mock_login_attempt)
        
        # Assert
        assert mock_login_attempt.attempts == 3
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    
    @patch('src.services.auth_service.db')
    def test_handle_failed_attempt_block_account(self, mock_db, mock_login_attempt):
        """
        Test: Bloquear cuenta después de 5 intentos
        Verifica que se establezca blocked_until
        """
        # Arrange
        email = 'test@example.com'
        mock_login_attempt.attempts = 4  # El siguiente será el 5to
        mock_login_attempt.blocked_until = None
        
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        
        # Act
        self.auth_service.handle_failed_attempt(email, mock_login_attempt)
        
        # Assert
        assert mock_login_attempt.attempts == 5
        assert mock_login_attempt.blocked_until is not None
        assert isinstance(mock_login_attempt.blocked_until, datetime)
    
    
    # ==================== TESTS DE GET_PROFILE ====================
    
    @patch('src.services.auth_service.execute_query')
    def test_get_profile_success(self, mock_execute_query, mock_user):
        """
        Test: Obtener perfil exitosamente
        """
        # Arrange
        user_id = 1
        mock_execute_query.return_value = {
            'success': True,
            'data': mock_user.to_dict()
        }
        
        # Act
        result = self.auth_service.get_profile(user_id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['id'] == user_id
        assert 'email' in result['data']
    
    
    @patch('src.services.auth_service.execute_query')
    def test_get_profile_user_not_found(self, mock_execute_query):
        """
        Test: Obtener perfil de usuario inexistente
        """
        # Arrange
        user_id = 999
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Usuario no encontrado',
            'data': None
        }
        
        # Act
        result = self.auth_service.get_profile(user_id)
        
        # Assert
        assert result['success'] is False
        assert 'no encontrado' in result['message'].lower()
    
    
    # ==================== TESTS DE UPDATE_PROFILE ====================
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_update_profile_success(self, mock_execute_transaction, mock_user):
        """
        Test: Actualizar perfil exitosamente
        """
        # Arrange
        user_id = 1
        update_data = {'name': 'Updated Name', 'email': 'updated@example.com'}
        
        updated_user = mock_user.to_dict()
        updated_user['name'] = update_data['name']
        updated_user['email'] = update_data['email']
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': updated_user
        }
        
        # Act
        result = self.auth_service.update_profile(user_id, update_data)
        
        # Assert
        assert result['success'] is True
        assert result['data']['name'] == update_data['name']
        assert result['data']['email'] == update_data['email']
    
    
    # ==================== TESTS DE CHANGE_PASSWORD ====================
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_change_password_success(self, mock_execute_transaction):
        """
        Test: Cambiar contraseña exitosamente
        """
        # Arrange
        user_id = 1
        current_password = 'OldPassword123!'
        new_password = 'NewPassword456!'
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'message': 'Contraseña actualizada exitosamente'}
        }
        
        # Act
        result = self.auth_service.change_password(user_id, current_password, new_password)
        
        # Assert
        assert result['success'] is True
        assert 'contraseña' in result['data']['message'].lower()
    
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_change_password_wrong_current_password(self, mock_execute_transaction):
        """
        Test: Cambiar contraseña con contraseña actual incorrecta
        """
        # Arrange
        user_id = 1
        current_password = 'WrongPassword'
        new_password = 'NewPassword456!'
        
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'La contraseña actual es incorrecta',
            'data': None
        }
        
        # Act
        result = self.auth_service.change_password(user_id, current_password, new_password)
        
        # Assert
        assert result['success'] is False
        assert 'incorrecta' in result['message'].lower()
    
    
    # ==================== TESTS DE DEACTIVATE_USER ====================
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_deactivate_user_success(self, mock_execute_transaction):
        """
        Test: Desactivar usuario exitosamente
        """
        # Arrange
        user_id = 1
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'message': 'Usuario desactivado exitosamente'}
        }
        
        # Act
        result = self.auth_service.deactivate_user(user_id)
        
        # Assert
        assert result['success'] is True
        assert 'desactivado' in result['data']['message'].lower()
    
    
    # ==================== TESTS DE ACTIVATE_USER ====================
    
    @patch('src.services.auth_service.execute_with_transaction')
    def test_activate_user_success(self, mock_execute_transaction):
        """
        Test: Activar usuario exitosamente
        """
        # Arrange
        user_id = 1
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'message': 'Usuario activado exitosamente'}
        }
        
        # Act
        result = self.auth_service.activate_user(user_id)
        
        # Assert
        assert result['success'] is True
        assert 'activado' in result['data']['message'].lower()