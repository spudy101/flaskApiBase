"""
Auth Controller - Request handlers
Equivalente a src/controllers/auth.controller.js
"""
from flask import request, g
from src.services.auth_service import auth_service
from src.dto.auth_dto import RegisterDTO, LoginDTO, RefreshTokenDTO
from src.utils.response_util import ApiResponse
from src.utils.app_error import AppError


class AuthController:
    """
    Auth controller
    Equivalente a AuthController en Node.js
    """
    
    def register(self):
        """
        POST /api/auth/register
        Registra un nuevo usuario
        """
        try:
            # Obtener datos del request
            data = request.get_json()
            
            # Crear DTO
            dto = RegisterDTO.from_request(data)
            
            # Audit context
            audit_context = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'method': request.method,
                'path': request.path
            }
            
            # Ejecutar servicio
            result = auth_service.register(dto, audit_context)
            
            # Respuesta
            return ApiResponse.created(
                'Usuario registrado exitosamente',
                result.to_dict()
            )
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def login(self):
        """
        POST /api/auth/login
        Login de usuario
        """
        try:
            data = request.get_json()
            dto = LoginDTO.from_request(data)
            
            audit_context = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'method': request.method,
                'path': request.path
            }
            
            result = auth_service.login(dto, audit_context)
            
            return ApiResponse.success(
                'Login exitoso',
                result.to_dict()
            )
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def logout(self):
        """
        POST /api/auth/logout
        Logout de usuario (requiere autenticación)
        """
        try:
            # Usuario viene del middleware de autenticación
            user = g.user
            token = g.token
            
            audit_context = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
            
            result = auth_service.logout(user['id'], token, audit_context)
            
            return ApiResponse.success('Logout exitoso', result)
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def refresh_token(self):
        """
        POST /api/auth/refresh
        Refresca el access token
        """
        try:
            data = request.get_json()
            dto = RefreshTokenDTO.from_request(data)
            
            audit_context = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
            
            result = auth_service.refresh_token(dto, audit_context)
            
            return ApiResponse.success(
                'Token refrescado exitosamente',
                result.to_dict()
            )
            
        except AppError as e:
            return ApiResponse.error(e.message, e.code, e.details, e.status_code)
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def me(self):
        """
        GET /api/auth/me
        Obtiene el usuario actual (requiere autenticación)
        """
        try:
            user = g.user
            return ApiResponse.success('Usuario obtenido', user)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))
    
    def verify_token(self):
        """
        GET /api/auth/verify
        Verifica si un token es válido
        """
        try:
            # Obtener token del header
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
            
            if not token:
                return ApiResponse.success('Token verification', {'valid': False, 'reason': 'No token provided'})
            
            result = auth_service.verify_token(token)
            
            return ApiResponse.success('Token verification', result)
            
        except Exception as e:
            return ApiResponse.internal_error(str(e))


# Singleton instance
auth_controller = AuthController()
