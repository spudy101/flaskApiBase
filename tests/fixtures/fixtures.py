"""
Test Fixtures - Reusable test data and helpers
"""
import pytest
from datetime import datetime
from src.models import User, Product, LoginAttempt


class MockUser:
    """Mock user for unit tests"""
    def __init__(self):
        self.id = 'uuid-test-123'
        self.email = 'test@example.com'
        self.name = 'Test User'
        self.role = 'user'
        self.is_active = True
        self.password = 'hashed-password'
        self.last_login = datetime.utcnow()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def check_password(self, password):
        return password == 'Password123!'
    
    def to_dict(self, exclude_password=True):
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if not exclude_password:
            data['password'] = self.password
        return data


@pytest.fixture
def mock_user():
    """Mock user fixture"""
    return MockUser()


@pytest.fixture
def sample_register_data():
    """Sample registration data"""
    return {
        'email': 'newuser@example.com',
        'password': 'Password123!',
        'name': 'New User',
        'role': 'user'
    }


@pytest.fixture
def sample_login_data():
    """Sample login data"""
    return {
        'email': 'test@example.com',
        'password': 'Password123!'
    }


@pytest.fixture
def sample_product_data():
    """Sample product data"""
    return {
        'name': 'Test Product',
        'description': 'Test description',
        'price': 99.99,
        'stock': 10,
        'category': 'Electronics'
    }


@pytest.fixture
def create_test_user(app):
    """Helper to create test user in database"""
    def _create_user(**kwargs):
        default_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'name': 'Test User',
            'role': 'user',
            'is_active': True
        }
        default_data.update(kwargs)
        
        user = User(**default_data)
        from config.database import db
        db.session.add(user)
        db.session.commit()
        return user
    
    return _create_user


@pytest.fixture
def create_test_product(app, create_test_user):
    """Helper to create test product in database"""
    def _create_product(user=None, **kwargs):
        if user is None:
            user = create_test_user()
        
        default_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 99.99,
            'stock': 10,
            'category': 'Electronics',
            'created_by': user.id
        }
        default_data.update(kwargs)
        
        product = Product(**default_data)
        from config.database import db
        db.session.add(product)
        db.session.commit()
        return product
    
    return _create_product


@pytest.fixture
def auth_headers(create_test_user):
    """Helper to get auth headers with valid token"""
    def _get_headers(user=None):
        if user is None:
            user = create_test_user()
        
        from src.utils.jwt_util import jwt_util
        tokens = jwt_util.generate_token_pair(user)
        
        return {
            'Authorization': f'Bearer {tokens["access_token"]}',
            'Content-Type': 'application/json'
        }
    
    return _get_headers
