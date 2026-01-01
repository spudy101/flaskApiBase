"""
Unit Tests - Auth DTOs
Equivalente a tests/unit/dto/auth.dto.test.js
"""
import pytest
from src.dto.auth_dto import (
    RegisterDTO,
    LoginDTO,
    RefreshTokenDTO,
    UserResponseDTO,
    TokensDTO,
    AuthResponseDTO
)
from tests.fixtures import mock_user


class TestRegisterDTO:
    """Test RegisterDTO"""
    
    def test_from_request_with_valid_data(self):
        """Test: should create DTO with valid data"""
        data = {
            'email': '  TEST@EXAMPLE.COM  ',
            'password': 'Password123!',
            'name': '  John Doe  ',
            'role': 'user'
        }
        
        dto = RegisterDTO.from_request(data)
        
        assert dto.email == 'test@example.com'  # lowercase + trimmed
        assert dto.password == 'Password123!'
        assert dto.name == 'John Doe'  # trimmed
        assert dto.role == 'user'
    
    def test_from_request_with_default_role(self):
        """Test: should set default role to user"""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'name': 'John Doe'
        }
        
        dto = RegisterDTO.from_request(data)
        
        assert dto.role == 'user'
    
    def test_from_request_handles_empty_email(self):
        """Test: should handle empty email"""
        data = {
            'email': '',
            'password': 'Password123!',
            'name': 'John Doe'
        }
        
        dto = RegisterDTO.from_request(data)
        
        assert dto.email == ''
    
    def test_to_dict_conversion(self):
        """Test: should convert to dictionary"""
        dto = RegisterDTO(
            email='test@example.com',
            password='Password123!',
            name='John Doe',
            role='user'
        )
        
        result = dto.to_dict()
        
        assert isinstance(result, dict)
        assert result['email'] == 'test@example.com'
        assert result['password'] == 'Password123!'


class TestLoginDTO:
    """Test LoginDTO"""
    
    def test_from_request_with_valid_credentials(self):
        """Test: should create DTO with valid credentials"""
        data = {
            'email': '  test@example.com  ',
            'password': 'Password123!'
        }
        
        dto = LoginDTO.from_request(data)
        
        assert dto.email == 'test@example.com'
        assert dto.password == 'Password123!'
    
    def test_from_request_with_uppercase_email(self):
        """Test: should lowercase email"""
        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'Password123!'
        }
        
        dto = LoginDTO.from_request(data)
        
        assert dto.email == 'test@example.com'


class TestRefreshTokenDTO:
    """Test RefreshTokenDTO"""
    
    def test_from_request_with_snake_case(self):
        """Test: should handle refresh_token (snake_case)"""
        data = {
            'refresh_token': 'valid-refresh-token'
        }
        
        dto = RefreshTokenDTO.from_request(data)
        
        assert dto.refresh_token == 'valid-refresh-token'
    
    def test_from_request_with_camel_case(self):
        """Test: should handle refreshToken (camelCase from Node.js)"""
        data = {
            'refreshToken': 'valid-refresh-token'
        }
        
        dto = RefreshTokenDTO.from_request(data)
        
        assert dto.refresh_token == 'valid-refresh-token'


class TestUserResponseDTO:
    """Test UserResponseDTO"""
    
    def test_from_model(self, mock_user):
        """Test: should create DTO from user model"""
        dto = UserResponseDTO.from_model(mock_user)
        
        assert dto.id == mock_user.id
        assert dto.email == mock_user.email
        assert dto.name == mock_user.name
        assert dto.role == mock_user.role
        assert dto.is_active == mock_user.is_active
    
    def test_to_dict_excludes_none_values(self, mock_user):
        """Test: should exclude None values from dict"""
        mock_user.last_login = None
        dto = UserResponseDTO.from_model(mock_user)
        
        result = dto.to_dict()
        
        assert 'last_login' not in result
        assert 'is_active' in result  # Always included even if False
    
    def test_to_dict_includes_all_fields(self, mock_user):
        """Test: should include all fields when present"""
        dto = UserResponseDTO.from_model(mock_user)
        
        result = dto.to_dict()
        
        assert 'id' in result
        assert 'email' in result
        assert 'name' in result
        assert 'role' in result
        assert 'is_active' in result
        assert 'created_at' in result
        assert 'updated_at' in result


class TestTokensDTO:
    """Test TokensDTO"""
    
    def test_creation(self):
        """Test: should create tokens DTO"""
        dto = TokensDTO(
            access_token='access-token-here',
            refresh_token='refresh-token-here'
        )
        
        assert dto.access_token == 'access-token-here'
        assert dto.refresh_token == 'refresh-token-here'
    
    def test_to_dict(self):
        """Test: should convert to dictionary"""
        dto = TokensDTO(
            access_token='access-token',
            refresh_token='refresh-token'
        )
        
        result = dto.to_dict()
        
        assert result == {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }


class TestAuthResponseDTO:
    """Test AuthResponseDTO"""
    
    def test_from_data(self, mock_user):
        """Test: should create DTO from user and tokens"""
        tokens = {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }
        
        dto = AuthResponseDTO.from_data(mock_user, tokens)
        
        assert isinstance(dto.user, UserResponseDTO)
        assert isinstance(dto.tokens, TokensDTO)
        assert dto.user.email == mock_user.email
        assert dto.tokens.access_token == 'access-token'
    
    def test_to_dict_structure(self, mock_user):
        """Test: should convert to nested dictionary"""
        tokens = {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token'
        }
        
        dto = AuthResponseDTO.from_data(mock_user, tokens)
        result = dto.to_dict()
        
        assert 'user' in result
        assert 'tokens' in result
        assert isinstance(result['user'], dict)
        assert isinstance(result['tokens'], dict)
