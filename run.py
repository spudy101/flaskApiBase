"""
Punto de entrada de la aplicación
Equivalente a server.js de Node.js
"""

import os
import sys
import signal
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.app import create_app
from config.database import db
from src.utils import logger

# Configuración
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Manejo de excepciones no capturadas"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error('Uncaught Exception', {
        'type': exc_type.__name__,
        'message': str(exc_value),
        'traceback': exc_traceback
    })


def graceful_shutdown(signum, frame):
    """Graceful shutdown del servidor"""
    signal_name = signal.Signals(signum).name
    logger.info(f'{signal_name} recibido, cerrando servidor...')
    
    try:
        # Cerrar conexión a base de datos
        db.session.remove()
        db.engine.dispose()
        logger.info('Conexión a BD cerrada')
        
        logger.info('Servidor cerrado exitosamente')
        sys.exit(0)
        
    except Exception as error:
        logger.error('Error al cerrar conexión a BD', {'error': str(error)})
        sys.exit(1)


def start_server():
    """Iniciar servidor"""
    try:
        # Crear aplicación
        app = create_app(FLASK_ENV)
        
        # Verificar conexión a base de datos
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            logger.info('✅ Conexión a base de datos exitosa', {
                'database': os.getenv('DB_NAME'),
                'host': os.getenv('DB_HOST')
            })
        
        # Configurar handlers de señales para graceful shutdown
        signal.signal(signal.SIGTERM, graceful_shutdown)
        signal.signal(signal.SIGINT, graceful_shutdown)
        
        # Configurar handler de excepciones no capturadas
        sys.excepthook = handle_uncaught_exception
        
        # Log de inicio
        logger.info('🚀 Servidor iniciado', {
            'port': PORT,
            'host': HOST,
            'environment': FLASK_ENV,
            'api_prefix': os.getenv('API_PREFIX', '/api/v1')
        })
        
        # Banner de inicio
        print('\n========================================')
        print(f'🚀 Servidor corriendo en puerto {PORT}')
        print(f'📊 Ambiente: {FLASK_ENV}')
        print(f'🔗 URL: http://{HOST}:{PORT}')
        print(f'🏥 Health: http://{HOST}:{PORT}{os.getenv("API_PREFIX", "/api/v1")}/health')
        print('========================================\n')
        
        # Iniciar servidor
        # En producción, usar Gunicorn o uWSGI en lugar del servidor de desarrollo
        if FLASK_ENV == 'production':
            logger.warning('⚠️  Usando servidor de desarrollo en producción. Usar Gunicorn o uWSGI.')
        
        app.run(
            host=HOST,
            port=PORT,
            debug=(FLASK_ENV == 'development'),
            use_reloader=(FLASK_ENV == 'development'),
            threaded=True
        )
        
    except Exception as error:
        logger.error('❌ Error al iniciar servidor', {
            'error': str(error),
            'type': type(error).__name__
        })
        sys.exit(1)


if __name__ == '__main__':
    start_server()