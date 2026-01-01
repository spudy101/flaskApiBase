"""
Integration Tests - Auth API
Equivalente a tests/integration/api/auth.test.js
"""
import pytest
import json
from src.models import User, LoginAttempt
from config.database import db


class TestAuthAPI:
    """Integration tests for Auth API endpoints"""
    
    def test_register_success(self, client, sample_register_data):
        """Test POST /api/auth/register - should register new user"""
        # Act
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_register_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'tokens' in data['data']
        assert data['data']['user']['email'] == 'newuser@example.com'
        assert 'password' not in data['data']['user']
        
        # Verificar que el usuario fue creado en DB
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
    
    def test_register_fails_with_duplicate_email(self, client, create_test_user, sample_register_data):
        """Test: should fail if email already exists"""
        # Arrange
        create_test_user(email='newuser@example.com')
        
        # Act
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_register_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
    
    def test_register_validates_email(self, client):
        """Test: should validate email format"""
        # Arrange
        invalid_data = {
            'email': 'not-an-email',
            'password': 'Password123!',
            'name': 'Test User'
        }
        
        # Act
        response = client.post(
            '/api/auth/register',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 422
        data = response.get_json()
        assert data['code'] == 'VALIDATION_ERROR'
    
    def test_register_validates_password_strength(self, client):
        """Test: should validate password strength"""
        # Arrange
        weak_password_data = {
            'email': 'test@example.com',
            'password': 'weak',  # Too short, no uppercase, no special char
            'name': 'Test User'
        }
        
        # Act
        response = client.post(
            '/api/auth/register',
            data=json.dumps(weak_password_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_login_success(self, client, create_test_user):
        """Test POST /api/auth/login - should login successfully"""
        # Arrange
        user = create_test_user(email='login@example.com', password='Password123!')
        login_data = {
            'email': 'login@example.com',
            'password': 'Password123!'
        }
        
        # Act
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'tokens' in data['data']
        assert data['data']['user']['email'] == 'login@example.com'
        
        # Verificar que last_login se actualizó
        db.session.refresh(user)
        assert user.last_login is not None
    
    def test_login_fails_with_invalid_email(self, client):
        """Test: should fail with invalid email"""
        # Arrange
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        # Act
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        
        # Verificar que se incrementaron los intentos
        attempt = LoginAttempt.query.filter_by(email='nonexistent@example.com').first()
        assert attempt is not None
        assert attempt.attempts == 1
    
    def test_login_fails_with_wrong_password(self, client, create_test_user):
        """Test: should fail with wrong password"""
        # Arrange
        create_test_user(email='test@example.com', password='Password123!')
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPassword!'
        }
        
        # Act
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_login_blocks_after_max_attempts(self, client, create_test_user):
        """Test: should block account after 5 failed attempts"""
        # Arrange
        create_test_user(email='block@example.com', password='Password123!')
        login_data = {
            'email': 'block@example.com',
            'password': 'WrongPassword!'
        }
        
        # Act - Make 5 failed attempts
        for i in range(5):
            client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
        
        # Act - 6th attempt (even with correct password)
        correct_data = {
            'email': 'block@example.com',
            'password': 'Password123!'
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(correct_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 429
        data = response.get_json()
        assert 'bloqueado' in data['message'].lower()
    
    def test_logout_success(self, client, auth_headers):
        """Test POST /api/auth/logout - should logout successfully"""
        # Arrange
        headers = auth_headers()
        
        # Act
        response = client.post(
            '/api/auth/logout',
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_logout_fails_without_token(self, client):
        """Test: should fail without token"""
        # Act
        response = client.post('/api/auth/logout')
        
        # Assert
        assert response.status_code == 401
    
    def test_refresh_token_success(self, client, create_test_user):
        """Test POST /api/auth/refresh - should refresh token"""
        # Arrange
        user = create_test_user()
        from src.utils.jwt_util import jwt_util
        tokens = jwt_util.generate_token_pair(user)
        
        refresh_data = {
            'refresh_token': tokens['refresh_token']
        }
        
        # Act
        response = client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'tokens' in data['data']
        assert data['data']['tokens']['access_token'] != tokens['access_token']
    
    def test_refresh_token_fails_with_invalid_token(self, client):
        """Test: should fail with invalid refresh token"""
        # Arrange
        refresh_data = {
            'refresh_token': 'invalid-token'
        }
        
        # Act
        response = client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_me_returns_current_user(self, client, auth_headers, create_test_user):
        """Test GET /api/auth/me - should return current user"""
        # Arrange
        user = create_test_user(email='me@example.com')
        headers = auth_headers(user)
        
        # Act
        response = client.get('/api/auth/me', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['email'] == 'me@example.com'
        assert 'password' not in data['data']
    
    def test_me_fails_without_auth(self, client):
        """Test: should fail without authentication"""
        # Act
        response = client.get('/api/auth/me')
        
        # Assert
        assert response.status_code == 401
    
    def test_verify_token_with_valid_token(self, client, auth_headers):
        """Test GET /api/auth/verify - should verify valid token"""
        # Arrange
        headers = auth_headers()
        
        # Act
        response = client.get('/api/auth/verify', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['valid'] is True
    
    def test_verify_token_with_invalid_token(self, client):
        """Test: should return invalid for bad token"""
        # Arrange
        headers = {
            'Authorization': 'Bearer invalid-token',
            'Content-Type': 'application/json'
        }
        
        # Act
        response = client.get('/api/auth/verify', headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['valid'] is False
