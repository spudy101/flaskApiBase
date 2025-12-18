"""
Configuración global de pytest para Flask
"""
import os
import pytest
from src.app import create_app
from src.database.connection import db

# Configurar variables de entorno para testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'test_user'
os.environ['DB_PASSWORD'] = 'test_password'
os.environ['DB_NAME'] = 'test_database'
os.environ['DB_PORT'] = '3306'
os.environ['DB_DIALECT'] = 'mysql'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
os.environ['AES_KEY'] = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
os.environ['AES_IV'] = '0123456789abcdef0123456789abcdef'
os.environ['RATE_LIMIT_ENABLED'] = 'False'  # Desactivar para tests

@pytest.fixture(scope='session')
def app():
    """Fixture de la aplicación Flask para toda la sesión de tests"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Usar base de datos en memoria para tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Fixture del cliente de prueba para cada test"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Fixture del CLI runner para tests de comandos"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Fixture de sesión de base de datos con rollback automático
    Cada test tiene su propia transacción que se revierte
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configurar sesión para usar esta transacción
        session = db.create_scoped_session(
            options={'bind': connection, 'binds': {}}
        )
        db.session = session
        
        yield session
        
        # Rollback y cleanup
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def auth_headers(app):
    """Fixture para generar headers de autenticación"""
    from flask_jwt_extended import create_access_token
    
    with app.app_context():
        # Crear un token de prueba
        access_token = create_access_token(identity={'id_usuario': 1, 'token': 'test-token'})
        return {
            'Authorization': f'Bearer {access_token}'
        }

@pytest.fixture
def sample_user_data():
    """Fixture con datos de usuario de ejemplo"""
    return {
        'id_usuario': 1,
        'id_rol': 1,
        'id_persona': 1,
        'run': '12345678-9',
        'nombres': 'Test',
        'apellidos': 'User',
        'correo': 'test@example.com',
        'telefono': '987654321',
        'token': 'test-token-123'
    }

@pytest.fixture
def mock_timestamp():
    """Fixture para generar timestamp encriptado válido"""
    from src.utils.crypto_utils import encriptar_mensaje
    import time
    
    timestamp = str(int(time.time() * 1000))
    return encriptar_mensaje(timestamp)
