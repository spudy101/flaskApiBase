import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # App
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123123')
    DB_SCHEMA = os.getenv('DB_SCHEMA', 'flask_schema')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Log queries
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 5,
        'pool_recycle': 3600,
        'max_overflow': 10,
        'connect_args': {
            'options': f'-csearch_path={DB_SCHEMA}'  # Equivalente a prependSearchPath
        }
    }
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    DB_SCHEMA = 'test'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}