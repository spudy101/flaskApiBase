import os

# Validar variables de entorno requeridas
required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_HOST']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")

# Configuración base para MySQL/PostgreSQL
def get_database_config():
    """Retorna la configuración de base de datos según el entorno"""
    
    db_dialect = os.getenv('DB_DIALECT', 'mysql').lower()
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 3306 if db_dialect == 'mysql' else 5432))
    db_name = os.getenv('DB_NAME')
    
    # Construir la URI de conexión
    if db_dialect == 'mysql':
        # MySQL con pymysql
        database_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    elif db_dialect == 'postgresql':
        # PostgreSQL
        database_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        raise ValueError(f"Dialecto de base de datos no soportado: {db_dialect}")
    
    # Configuración común
    base_config = {
        'SQLALCHEMY_DATABASE_URI': database_uri,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ECHO': os.getenv('DB_DEBUG', 'False').lower() == 'true',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_size': 5,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'max_overflow': 10,
            'echo_pool': os.getenv('DB_DEBUG', 'False').lower() == 'true',
            'connect_args': {
                'connect_timeout': 30,
            }
        }
    }
    
    # Ajustes específicos por dialecto
    if db_dialect == 'mysql':
        base_config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args'].update({
            'charset': 'utf8mb4',
        })
    
    return base_config

# Configuraciones por entorno
class DevelopmentConfig:
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    config = get_database_config()
    config['SQLALCHEMY_ECHO'] = True
    
    @classmethod
    def get_config(cls):
        return cls.config

class ProductionConfig:
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    config = get_database_config()
    config['SQLALCHEMY_ECHO'] = False
    
    @classmethod
    def get_config(cls):
        return cls.config

class TestingConfig:
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    config = get_database_config()
    
    @classmethod
    def get_config(cls):
        return cls.config

# Mapeo de configuraciones
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'production')
    return config_by_name.get(env, ProductionConfig).get_config()
