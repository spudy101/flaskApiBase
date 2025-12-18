import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.app import create_app
from src.database.connection import init_db, close_db

def start_server():
    """Inicializa y ejecuta el servidor Flask"""
    try:
        # Inicializar la base de datos
        db_ready = init_db()
        if not db_ready:
            raise Exception("No se pudo conectar a la base de datos")
        
        # Crear la aplicación Flask
        app = create_app()
        
        # Obtener configuración del servidor
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"🚀 Servidor Flask corriendo en {host}:{port}")
        print(f"📊 Entorno: {os.getenv('FLASK_ENV', 'production')}")
        print(f"🔧 Debug mode: {debug}")
        
        # Ejecutar el servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except Exception as error:
        print(f"❌ Error al inicializar: {str(error)}")
        exit(1)
    finally:
        # Cerrar conexión a la base de datos al finalizar
        close_db()

if __name__ == '__main__':
    start_server()
