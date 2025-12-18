"""
Registro de rutas (Blueprints)
Equivalente a src/routes/index.js
"""
from flask import Flask
from .perfil_routes import perfil_bp

def register_routes(app: Flask):
    """
    Registra todos los blueprints en la aplicación
    Equivalente a app.use() de Express
    
    Args:
        app: Instancia de Flask
    """
    
    # Registrar blueprints (equivalente a router.use() de Express)
    app.register_blueprint(perfil_bp)
    
    print("✅ Rutas registradas:")
    print("   - /perfil_usuario/*")
    
    # Aquí puedes agregar más blueprints:
    # from .auth_routes import auth_bp
    # app.register_blueprint(auth_bp)

__all__ = ['register_routes']
