"""
Controller de usuarios
Equivalente a userController.js
"""

from src.services import user_service, auth_service
from src.utils import success_response, error_response, paginated_response, logger


class UserController:
    """Controller de usuarios"""
    
    def list_users(self, req):
        """
        Listar todos los usuarios (Admin)
        GET /api/v1/users
        """
        try:
            filters = {
                'page': req.args.get('page'),
                'limit': req.args.get('limit'),
                'role': req.args.get('role'),
                'isActive': req.args.get('isActive'),
                'search': req.args.get('search')
            }
            
            result = user_service.list_users(filters)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return paginated_response(
                result['data']['users'],
                result['data']['pagination']['page'],
                result['data']['pagination']['limit'],
                result['data']['pagination']['total'],
                'Usuarios obtenidos exitosamente'
            )
            
        except Exception as error:
            logger.error(f'Error en listUsers controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def get_user_by_id(self, req, user_id):
        """
        Obtener usuario por ID (Admin)
        GET /api/v1/users/:id
        """
        try:
            result = user_service.get_user_by_id(user_id)
            
            if not result['success']:
                return error_response(result['message'], 404)
            
            return success_response(
                result['data'],
                'Usuario obtenido exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getUserById controller: {str(error)}')
            
            if str(error) == 'Usuario no encontrado':
                return error_response(str(error), 404)
            
            return error_response(str(error), 500)
    
    
    def update_user_role(self, req, user_id):
        """
        Actualizar rol de usuario (Admin)
        PUT /api/v1/users/:id/role
        """
        try:
            data = req.get_json()
            role = data.get('role')
            
            result = user_service.update_user_role(user_id, role)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Rol actualizado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en updateUserRole controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def activate_user(self, req, user_id):
        """
        Activar usuario (Admin)
        PUT /api/v1/users/:id/activate
        """
        try:
            result = auth_service.activate_user(user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Usuario activado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en activateUser controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def deactivate_user(self, req, user_id):
        """
        Desactivar usuario (Admin)
        PUT /api/v1/users/:id/deactivate
        """
        try:
            result = auth_service.deactivate_user(user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Usuario desactivado exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en deactivateUser controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def delete_user(self, req, user_id):
        """
        Eliminar usuario permanentemente (Admin)
        DELETE /api/v1/users/:id
        """
        try:
            result = user_service.delete_user(user_id)
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Usuario eliminado permanentemente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en deleteUser controller: {str(error)}')
            return error_response(str(error), 500)
    
    
    def get_user_stats(self, req):
        """
        Obtener estadísticas de usuarios (Admin)
        GET /api/v1/users/stats
        """
        try:
            result = user_service.get_user_stats()
            
            if not result['success']:
                return error_response(result['message'], 400)
            
            return success_response(
                result['data'],
                'Estadísticas obtenidas exitosamente',
                200
            )
            
        except Exception as error:
            logger.error(f'Error en getUserStats controller: {str(error)}')
            return error_response(str(error), 500)


# Exportar instancia única
user_controller = UserController()