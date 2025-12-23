"""
Configuración para tests unitarios
Fixtures específicas para tests con mocks
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta


@pytest.fixture
def mock_db_session():
    """
    Mock de sesión de base de datos
    Útil para tests unitarios que no deben tocar la DB real
    """
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.flush = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_user():
    """
    Mock de modelo User
    """
    user = Mock()
    user.id = 1
    user.email = 'test@example.com'
    user.name = 'Test User'
    user.role = 'user'
    user.is_active = True
    user.last_login = datetime.utcnow()
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    # Métodos
    user.compare_password = Mock(return_value=True)
    user.to_dict = Mock(return_value={
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'is_active': user.is_active,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    })
    
    return user


@pytest.fixture
def mock_login_attempt():
    """
    Mock de modelo LoginAttempt
    """
    attempt = Mock()
    attempt.email = 'test@example.com'
    attempt.attempts = 0
    attempt.blocked_until = None
    attempt.ip_address = '127.0.0.1'
    return attempt


@pytest.fixture
def mock_execute_with_transaction():
    """
    Mock de la función execute_with_transaction
    Simula ejecución exitosa por defecto
    """
    with patch('src.services.auth_service.execute_with_transaction') as mock:
        mock.return_value = {
            'success': True,
            'data': {},
            'message': 'Operación exitosa'
        }
        yield mock


@pytest.fixture
def mock_execute_query():
    """
    Mock de la función execute_query
    Simula ejecución exitosa por defecto
    """
    with patch('src.services.auth_service.execute_query') as mock:
        mock.return_value = {
            'success': True,
            'data': {},
            'message': 'Query exitoso'
        }
        yield mock


@pytest.fixture
def mock_generate_token():
    """
    Mock de la función generate_token
    """
    with patch('src.services.auth_service.generate_token') as mock:
        mock.return_value = 'mock-jwt-token-12345'
        yield mock


@pytest.fixture
def mock_logger():
    """
    Mock del logger para verificar que se loguean eventos importantes
    """
    with patch('src.services.auth_service.logger') as mock:
        yield mock


@pytest.fixture
def sample_user_data():
    """
    Datos de ejemplo para crear un usuario
    """
    return {
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'name': 'New User',
        'role': 'user'
    }


@pytest.fixture
def sample_login_data():
    """
    Datos de ejemplo para login
    """
    return {
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    }