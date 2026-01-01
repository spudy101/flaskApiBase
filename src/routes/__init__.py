"""
Routes package - Register all blueprints
Equivalente a combinar todas las routes en Express
"""
from .auth_routes import auth_bp
from .user_routes import user_bp
from .product_routes import product_bp


def register_blueprints(app):
    """
    Registra todos los blueprints en la aplicación
    Equivalente a app.use() en Express
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'API is running'}, 200


__all__ = ['register_blueprints', 'auth_bp', 'user_bp', 'product_bp']
