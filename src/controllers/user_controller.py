"""
User Controller
Equivalente a src/controllers/user.controller.js
"""
from flask import request, g
from src.repositories.user_repository import user_repository
from src.dto.user_dto import UpdateUserDTO
from src.dto.auth_dto import UserResponseDTO
from src.utils.response_util import ApiResponse
from src.utils.app_error import AppError


class UserController:
    """User controller"""
    
    def get_all(self):
        """
        GET /api/users
        Obtiene todos los usuarios (requiere auth)
        """
        try:
            # Parámetros de paginación
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            
            # Obtener usuarios
            result = user_repository.find_with_pagination(page=page, limit=limit)
            
            # Convertir a DTOs
            users_dto = [UserResponseDTO.from_model(user).to_dict() for user in result['rows']]
            
            response_data = {
                'users': users_dto,
                'pagination': {
                    'page': result['page'],
                    'limit': result['limit'],
                    'total': result['count'],
                    'total_pages': result['total_pages']
                }
            }
            
            return ApiResponse.success('Usuarios obtenidos', response_data)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def get_by_id(self, user_id: str):
        """
        GET /api/users/:id
        Obtiene un usuario por ID
        """
        try:
            user = user_repository.find_by_id(user_id)
            
            if not user:
                return ApiResponse.not_found('Usuario no encontrado')
            
            user_dto = UserResponseDTO.from_model(user).to_dict()
            
            return ApiResponse.success('Usuario obtenido', user_dto)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def update(self, user_id: str):
        """
        PUT /api/users/:id
        Actualiza un usuario
        """
        try:
            # Verificar permisos: solo el mismo usuario o admin
            current_user = g.user
            if current_user['id'] != user_id and current_user['role'] != 'admin':
                return ApiResponse.forbidden('No tienes permisos para actualizar este usuario')
            
            # Obtener datos
            data = request.get_json()
            dto = UpdateUserDTO.from_request(data)
            
            # Si hay password, hashearlo
            update_data = dto.to_dict()
            if 'password' in update_data and update_data['password']:
                # El model se encargará del hash
                pass
            
            # Actualizar
            updated_user = user_repository.update(user_id, update_data)
            
            if not updated_user:
                return ApiResponse.not_found('Usuario no encontrado')
            
            user_dto = UserResponseDTO.from_model(updated_user).to_dict()
            
            return ApiResponse.success('Usuario actualizado', user_dto)
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def delete(self, user_id: str):
        """
        DELETE /api/users/:id
        Elimina (desactiva) un usuario
        """
        try:
            # Solo admin puede eliminar
            current_user = g.user
            if current_user['role'] != 'admin':
                return ApiResponse.forbidden('Solo administradores pueden eliminar usuarios')
            
            # Soft delete
            success = user_repository.deactivate(user_id)
            
            if not success:
                return ApiResponse.not_found('Usuario no encontrado')
            
            return ApiResponse.success('Usuario eliminado')
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))


# Singleton instance
user_controller = UserController()
