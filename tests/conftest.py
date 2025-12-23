"""
Configuración global de pytest
Fixtures compartidas por todos los tests
"""

import pytest
import sys
import os

# ===============================
# Variables de entorno para tests
# ===============================
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key")
os.environ.setdefault("FLASK_ENV", "test")
os.environ.setdefault("DB_SCHEMA", "test")

# Agregar src al path para imports
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from src.app import create_app
from config.database import db as _db
from config.settings import config


@pytest.fixture(scope='session')
def app():
    """
    Crea una instancia de la aplicación Flask configurada para testing
    Scope: session - se crea una vez por sesión de tests
    """
    # Crear app con configuración de test
    test_app = create_app(env='test')
    test_app.config.from_object(config['test'])
    
    # Establecer contexto de aplicación
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope='session')
def db(app):
    """
    Crea y configura la base de datos para tests
    Scope: session - la estructura de DB se crea una vez
    """
    # Crear todas las tablas
    _db.create_all()
    
    yield _db
    
    # Cleanup: eliminar todas las tablas al final de la sesión
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Crea una sesión de base de datos para cada test
    Scope: function - se crea una nueva sesión por test
    Hace rollback automático después de cada test
    """
    # Iniciar transacción
    connection = db.engine.connect()
    transaction = connection.begin()

    # Rebindear la sesión actual a esta conexión
    db.session.bind = connection

    yield db.session

    # Rollback
    db.session.rollback()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def client(app, session):
    """
    Crea un cliente de test de Flask
    Scope: function - nuevo cliente por test
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Crea un CLI runner para tests de comandos
    Scope: function - nuevo runner por test
    """
    return app.test_cli_runner()