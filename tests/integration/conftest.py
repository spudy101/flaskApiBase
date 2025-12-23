"""
Configuración para tests de integración
Fixtures específicas para tests con base de datos real
"""

import pytest
from datetime import datetime
from src.models.user import User
from src.models import LoginAttempt
from src.utils import generate_token

# Importar fixtures adicionales
pytest_plugins = [
    'tests.integration.fixtures.products_fixtures',
]


@pytest.fixture
def create_user(session):
    """
    Factory fixture para crear usuarios en la base de datos
    Retorna una función que crea usuarios
    """
    created_users = []
    
    def _create_user(email='test@example.com', password='SecurePass123!', 
                     name='Test User', role='user', is_active=True):
        """Crea un usuario en la base de datos"""
        user = User(
            email=email,
            password=password,
            name=name,
            role=role,
            is_active=is_active
        )
        session.add(user)
        session.commit()
        session.refresh(user)  # Refrescar para obtener datos actualizados
        created_users.append(user)
        return user
    
    yield _create_user
    
    # Cleanup: eliminar usuarios creados
    for user in created_users:
        session.delete(user)
    session.commit()


@pytest.fixture
def test_user(create_user):
    """
    Usuario de prueba pre-creado
    Útil para tests que necesitan un usuario existente
    """
    return create_user(
        email='testuser@example.com',
        password='TestPassword123!',
        name='Test User',
        role='user'
    )


@pytest.fixture
def admin_user(create_user):
    """
    Usuario administrador de prueba
    """
    return create_user(
        email='admin@example.com',
        password='AdminPassword123!',
        name='Admin User',
        role='admin'
    )


@pytest.fixture
def inactive_user(create_user):
    """
    Usuario inactivo de prueba
    """
    return create_user(
        email='inactive@example.com',
        password='InactivePassword123!',
        name='Inactive User',
        role='user',
        is_active=False
    )


@pytest.fixture
def auth_token(test_user):
    """
    Token JWT válido para un usuario de prueba
    """
    return generate_token({
        'id': test_user.id,
        'email': test_user.email,
        'role': test_user.role
    })


@pytest.fixture
def auth_headers(auth_token):
    """
    Headers de autorización con token válido
    Formato: {'Authorization': 'Bearer <token>'}
    """
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def create_login_attempt(session):
    """
    Factory fixture para crear intentos de login
    """
    created_attempts = []
    
    def _create_login_attempt(email='test@example.com', attempts=0, 
                              blocked_until=None, ip_address='127.0.0.1'):
        """Crea un intento de login en la base de datos"""
        login_attempt = LoginAttempt(
            email=email,
            attempts=attempts,
            blocked_until=blocked_until,
            ip_address=ip_address
        )
        session.add(login_attempt)
        session.commit()
        session.refresh(login_attempt)
        created_attempts.append(login_attempt)
        return login_attempt
    
    yield _create_login_attempt
    
    # Cleanup
    for attempt in created_attempts:
        session.delete(attempt)
    session.commit()


@pytest.fixture
def sample_register_payload():
    """
    Payload válido para registro de usuario
    """
    return {
        'email': 'newuser@example.com',
        'password': 'NewUserPass123!',
        'name': 'New User',
        'role': 'user'
    }


@pytest.fixture
def sample_login_payload():
    """
    Payload válido para login
    """
    return {
        'email': 'testuser@example.com',
        'password': 'TestPassword123!'
    }


@pytest.fixture
def sample_update_profile_payload():
    """
    Payload válido para actualizar perfil
    """
    return {
        'name': 'Updated Name',
        'email': 'updated@example.com'
    }


@pytest.fixture
def sample_change_password_payload():
    """
    Payload válido para cambiar contraseña
    """
    return {
        'currentPassword': 'TestPassword123!',
        'newPassword': 'NewSecurePass456!'
    }