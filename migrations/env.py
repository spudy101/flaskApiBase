from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Agregar el directorio raíz al path para importar nuestros módulos
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importar configuración y modelos
from config.settings import config as app_config
from config.database import db

# Obtener configuración de Flask
env = os.getenv('FLASK_ENV', 'development')
flask_config = app_config[env]

# Configuración de Alembic
config = context.config

# Interpretar el archivo de configuración para logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos (para autogenerate)
# IMPORTANTE: Importar todos los modelos aquí
from src.models import User, Product, LoginAttempt

target_metadata = db.metadata

# Configurar la URL de la base de datos desde nuestro settings
config.set_main_option('sqlalchemy.url', flask_config.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline() -> None:
    """
    Ejecutar migrations en modo 'offline'.
    No necesita conexión a BD, genera SQL scripts.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=flask_config.DB_SCHEMA,  # Schema personalizado
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migrations en modo 'online'.
    Conecta a la BD y ejecuta las migrations.
    """
    # Configuración del engine con opciones de conexión
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = flask_config.SQLALCHEMY_DATABASE_URI
    
    # Agregar opciones para el schema
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={'options': f'-csearch_path={flask_config.DB_SCHEMA}'}
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=flask_config.DB_SCHEMA,  # Tabla de versiones en el schema
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()