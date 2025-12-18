import os
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, text
from src.config.database import get_config

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def init_db():
    """
    Inicializa y prueba la conexión a la base de datos
    Equivalente a initializeDatabase() de Node.js
    """
    try:
        # Obtener configuración
        config = get_config()
        
        print(f"🔍 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Probando conexión a BD...")
        start_time = time.time()
        
        # Probar la conexión
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        connection_time = (time.time() - start_time) * 1000
        
        print(f"✅ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Conexión exitosa en {connection_time:.2f}ms")
        print(f"📊 Entorno: {os.getenv('FLASK_ENV', 'production')}")
        print(f"🗄️ Base de datos: {os.getenv('DB_NAME')}")
        print(f"🌐 Host: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        
        return True
    except Exception as error:
        connection_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        print(f"❌ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Error de conexión ({connection_time:.2f}ms):")
        print(f"   Mensaje: {str(error)}")
        print(f"   Host: {os.getenv('DB_HOST')}")
        print(f"   Base de datos: {os.getenv('DB_NAME')}")
        return False

def setup_db_events():
    """Configura eventos de base de datos para debugging"""
    if os.getenv('DB_DEBUG', 'False').lower() == 'true':
        
        @event.listens_for(db.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            print(f"🔍 [DB] {statement}")
        
        @event.listens_for(db.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
            print(f"⏱️ [DB] Query ejecutado")
        
        @event.listens_for(db.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            print(f"🔄 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Nueva conexión a BD establecida")
        
        @event.listens_for(db.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            print(f"❌ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Conexión a BD cerrada")

def get_pool_stats():
    """
    Obtiene estadísticas del pool de conexiones
    Equivalente a getPoolStats() de Node.js
    """
    try:
        pool = db.engine.pool
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'max_overflow': pool._max_overflow
        }
    except Exception as error:
        return {'error': f'Error obteniendo estadísticas del pool: {str(error)}'}

def validate_connection():
    """
    Valida que la conexión a la base de datos esté activa
    Equivalente a validateConnection() de Node.js
    """
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as error:
        print(f"❌ Error de conexión a BD: {str(error)}")
        return False

def close_db():
    """
    Cierra la conexión a la base de datos
    Equivalente a closeConnection() de Node.js
    """
    try:
        print("🔄 Cerrando conexión a base de datos...")
        db.session.remove()
        db.engine.dispose()
        print("✅ Conexión cerrada correctamente")
    except Exception as error:
        print(f"❌ Error al cerrar conexión: {str(error)}")

# Para importar en otros módulos
__all__ = ['db', 'init_db', 'close_db', 'validate_connection', 'get_pool_stats', 'setup_db_events']
