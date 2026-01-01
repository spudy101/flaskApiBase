"""
Auth Routes - Flask Blueprint
Equivalente a src/routes/auth.routes.js
"""
from flask import Blueprint
from src.controllers.auth_controller import auth_controller
from src.middlewares.auth_middleware import authenticate
from src.validators.auth_validator import validate_register, validate_login, validate_refresh_token

# Crear blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@validate_register()
def register():
    """POST /api/auth/register - Registrar usuario"""
    return auth_controller.register()


@auth_bp.route('/login', methods=['POST'])
@validate_login()
def login():
    """POST /api/auth/login - Login"""
    return auth_controller.login()


@auth_bp.route('/logout', methods=['POST'])
@authenticate()
def logout():
    """POST /api/auth/logout - Logout (requiere auth)"""
    return auth_controller.logout()


@auth_bp.route('/refresh', methods=['POST'])
@validate_refresh_token()
def refresh():
    """POST /api/auth/refresh - Refresh token"""
    return auth_controller.refresh_token()


@auth_bp.route('/me', methods=['GET'])
@authenticate()
def me():
    """GET /api/auth/me - Usuario actual (requiere auth)"""
    return auth_controller.me()


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """GET /api/auth/verify - Verificar token"""
    return auth_controller.verify_token()
