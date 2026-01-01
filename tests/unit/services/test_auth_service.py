"""
Unit Tests - Auth Service
Equivalente a tests/unit/services/auth.service.test.js
"""
import pytest
from unittest.mock import Mock, patch
import jwt as pyjwt
from src.services.auth_service import auth_service
from src.dto.auth_dto import RegisterDTO, LoginDTO, RefreshTokenDTO
from src.utils.app_error import AppError
from tests.fixtures import mock_user


class TestAuthService:
    """Test AuthService"""
    
    @patch('src.services.auth_service.user_repository')
    @patch('src.services.auth_service.jwt_util')
    def test_register_success(self, mock_jwt, mock_repo, sample_register_data, mock_user):
        """Test: should register new user successfully"""
        # Arrange
        dto = RegisterDTO.from_request(sample_register_data)
        audit_context = {'ip': '127.0.0.1', 'user_agent': 'pytest'}
        
        mock_repo.find_by_email.return_value = None
        mock_repo.create.return_value = mock_user
        mock_jwt.generate_token_pair.return_value = {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }
        
        # Act
        result = auth_service.register(dto, audit_context)
        
        # Assert
        assert result is not None
        mock_repo.find_by_email.assert_called_once_with('newuser@example.com')
        mock_repo.create.assert_called_once()
        mock_jwt.generate_token_pair.assert_called_once()
    
    @patch('src.services.auth_service.user_repository')
    def test_register_fails_if_email_exists(self, mock_repo, sample_register_data, mock_user):
        """Test: should throw conflict error if email exists"""
        # Arrange
        dto = RegisterDTO.from_request(sample_register_data)
        audit_context = {'ip': '127.0.0.1'}
        
        mock_repo.find_by_email.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            auth_service.register(dto, audit_context)
        
        assert exc_info.value.status_code == 409
        mock_repo.create.assert_not_called()
    
    @patch('src.services.auth_service.login_attempts_repository')
    @patch('src.services.auth_service.user_repository')
    @patch('src.services.auth_service.jwt_util')
    def test_login_success(self, mock_jwt, mock_user_repo, mock_attempts, sample_login_data, mock_user):
        """Test: should login successfully with valid credentials"""
        # Arrange
        dto = LoginDTO.from_request(sample_login_data)
        audit_context = {'ip': '127.0.0.1'}
        
        mock_attempts.is_blocked.return_value = False
        mock_user_repo.find_active_by_email.return_value = mock_user
        mock_user_repo.update_last_login.return_value = True
        mock_jwt.generate_token_pair.return_value = {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }
        
        # Act
        result = auth_service.login(dto, audit_context)
        
        # Assert
        assert result is not None
        mock_attempts.is_blocked.assert_called_once()
        mock_user_repo.find_active_by_email.assert_called_once()
        mock_attempts.reset_attempts.assert_called_once()
        mock_user_repo.update_last_login.assert_called_once()
    
    @patch('src.services.auth_service.login_attempts_repository')
    def test_login_fails_if_blocked(self, mock_attempts, sample_login_data):
        """Test: should fail if account is blocked"""
        # Arrange
        dto = LoginDTO.from_request(sample_login_data)
        audit_context = {'ip': '127.0.0.1'}
        
        mock_attempts.is_blocked.return_value = True
        mock_attempts.get_remaining_block_time.return_value = 600  # 10 min
        
        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            auth_service.login(dto, audit_context)
        
        assert exc_info.value.status_code == 429
    
    @patch('src.services.auth_service.login_attempts_repository')
    @patch('src.services.auth_service.user_repository')
    def test_login_fails_with_invalid_credentials(self, mock_user_repo, mock_attempts, sample_login_data):
        """Test: should fail with invalid credentials"""
        # Arrange
        dto = LoginDTO.from_request(sample_login_data)
        audit_context = {'ip': '127.0.0.1'}
        
        mock_attempts.is_blocked.return_value = False
        mock_user_repo.find_active_by_email.return_value = None
        
        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            auth_service.login(dto, audit_context)
        
        assert exc_info.value.status_code == 401
        mock_attempts.increment_attempts.assert_called_once()
    
    @patch('src.services.auth_service.login_attempts_repository')
    @patch('src.services.auth_service.user_repository')
    def test_login_fails_with_wrong_password(self, mock_user_repo, mock_attempts, sample_login_data, mock_user):
        """Test: should fail with wrong password"""
        # Arrange
        dto = LoginDTO(email='test@example.com', password='WrongPassword!')
        audit_context = {'ip': '127.0.0.1'}
        
        mock_attempts.is_blocked.return_value = False
        mock_user_repo.find_active_by_email.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            auth_service.login(dto, audit_context)
        
        assert exc_info.value.status_code == 401
        mock_attempts.increment_attempts.assert_called_once()
    
    def test_logout_success(self):
        """Test: should logout successfully"""
        # Arrange
        user_id = 'uuid-123'
        token = 'access-token'
        audit_context = {'ip': '127.0.0.1'}
        
        # Act
        result = auth_service.logout(user_id, token, audit_context)
        
        # Assert
        assert result is not None
        assert 'message' in result
    
    @patch('src.services.auth_service.user_repository')
    @patch('src.services.auth_service.jwt_util')
    def test_refresh_token_success(self, mock_jwt, mock_repo, mock_user):
        """Test: should refresh token successfully"""
        # Arrange
        dto = RefreshTokenDTO(refresh_token='valid-refresh-token')
        audit_context = {'ip': '127.0.0.1'}
        
        mock_jwt.verify_refresh_token.return_value = {'id': 'uuid-123'}
        mock_repo.find_by_id.return_value = mock_user
        mock_jwt.generate_token_pair.return_value = {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token'
        }
        
        # Act
        result = auth_service.refresh_token(dto, audit_context)
        
        # Assert
        assert result is not None
        mock_jwt.verify_refresh_token.assert_called_once()
        mock_repo.find_by_id.assert_called_once()
    
    @patch('src.services.auth_service.jwt_util')
    def test_refresh_token_fails_with_expired_token(self, mock_jwt):
        """Test: should fail with expired token"""
        # Arrange
        dto = RefreshTokenDTO(refresh_token='expired-token')
        audit_context = {'ip': '127.0.0.1'}
        
        mock_jwt.verify_refresh_token.side_effect = pyjwt.ExpiredSignatureError
        
        # Act & Assert
        with pytest.raises(AppError) as exc_info:
            auth_service.refresh_token(dto, audit_context)
        
        assert exc_info.value.status_code == 401
    
    @patch('src.services.auth_service.user_repository')
    @patch('src.services.auth_service.jwt_util')
    def test_verify_token_success(self, mock_jwt, mock_repo, mock_user):
        """Test: should verify valid token"""
        # Arrange
        token = 'valid-token'
        
        mock_jwt.verify_access_token.return_value = {'id': 'uuid-123'}
        mock_repo.find_by_id.return_value = mock_user
        
        # Act
        result = auth_service.verify_token(token)
        
        # Assert
        assert result['valid'] is True
        assert 'user' in result
    
    @patch('src.services.auth_service.jwt_util')
    def test_verify_token_fails_with_expired_token(self, mock_jwt):
        """Test: should return invalid for expired token"""
        # Arrange
        token = 'expired-token'
        
        mock_jwt.verify_access_token.side_effect = pyjwt.ExpiredSignatureError
        
        # Act
        result = auth_service.verify_token(token)
        
        # Assert
        assert result['valid'] is False
        assert 'reason' in result
