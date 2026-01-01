"""
Run Flask Application
Entry point de la aplicación
"""
from src.app import create_app
import os

# Crear app
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Configuración del servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = env == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║        🐍 FLASK API SERVER 🐍           ║
    ║                                          ║
    ║  Environment: {env:^27} ║
    ║  Host:        {host:^27} ║
    ║  Port:        {str(port):^27} ║
    ║  Debug:       {str(debug):^27} ║
    ║                                          ║
    ║  Ready: http://{host}:{port}              ║
    ║  Health: http://{host}:{port}/health      ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
