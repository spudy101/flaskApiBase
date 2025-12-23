"""
Controller de autenticación
Equivalente a authController.js
"""

from src.services import auth_service
from src.utils import success_response, error_response, logger


class AuthController:
    """Controller de autenticación"""
    
    def register(self, req):
        """
        Registrar nuevo usuario
        POST /api/v1/auth/register
        """
        try:
            data = req.get_json()
            
            result = auth_service.register({
                'email': data.get('email'),
                'password': data.get('password'),
                'name': data.get('name'),
                'role': data.get('role')
            })
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            logger.info('Usuario registrado desde controller', extra={
                'email': result['data']['user']['email']
            })
            
            return success_response(
                result['data'],
                'Usuario registrado exitosamente',
                201
            )
            
        except Exception as error:
            logger.error(f'Error en register controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def login(self, req):
        """
        Login de usuario
        POST /api/v1/auth/login
        """
        try:
            data = req.get_json()
            
            result = auth_service.login(
                data.get('email'),
                data.get('password')
            )
            
            if not result['success']:
                return error_response(result['message'], 401)
            
            logger.info('Usuario logueado desde controller', extra={
                'email': result['data']['user']['email']
            })
            
            return success_response(
                result['data'],
                'Inicio de sesión exitoso',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en login controller: {str(error)}')
            
            # Errores específicos de login
            error_message = str(error)
            if error_message in ['Credenciales inválidas', 'Usuario inactivo'] or 'bloqueada' in error_message:
                return error_response(error_message, 401)
            
            return error_response(str(error), 500)
    
    
    def get_profile(self, req):
        """
        Obtener perfil del usuario autenticado
        GET /api/v1/auth/profile
        """
        try:
            user_id = req.user['id']
            
            result = auth_service.get_profile(user_id)
            
            if not result['success']:
                return error_response(result['message'], 404)
            
            return success_response(
                result['data'],
                'Perfil obtenido exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getProfile controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def update_profile(self, req):
        """
        Actualizar perfil del usuario autenticado
        PUT /api/v1/auth/profile
        """
        try:
            user_id = req.user['id']
            data = req.get_json()
            
            result = auth_service.update_profile(user_id, {
                'name': data.get('name'),
                'email': data.get('email')
            })
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Perfil actualizado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en updateProfile controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def change_password(self, req):
        """
        Cambiar contraseña del usuario autenticado
        PUT /api/v1/auth/change-password
        """
        try:
            user_id = req.user['id']
            data = req.get_json()
            
            result = auth_service.change_password(
                user_id,
                data.get('currentPassword'),
                data.get('newPassword')
            )
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Contraseña actualizada exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en changePassword controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def deactivate_account(self, req):
        """
        Desactivar cuenta del usuario autenticado
        DELETE /api/v1/auth/account
        """
        try:
            user_id = req.user['id']
            
            result = auth_service.deactivate_user(user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Cuenta desactivada exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en deactivateAccount controller: {str(error)}')
            return error_response(str(error), 500)