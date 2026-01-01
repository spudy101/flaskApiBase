"""
Auth Service - Authentication business logic
Equivalente a src/services/auth.service.js
"""
from typing import Dict
import jwt as pyjwt
from src.dto.auth_dto import RegisterDTO, LoginDTO, RefreshTokenDTO, AuthResponseDTO
from src.repositories.user_repository import user_repository
from src.repositories.login_attempts_repository import login_attempts_repository
from src.utils.app_error import AppError
from src.utils.jwt_util import jwt_util
from src.utils.logger_util import logger


class AuthService:
    """
    Authentication service
    Equivalente a AuthService en Node.js
    """
    
    def __init__(self):
        self.user_repo = user_repository
        self.login_attempts_repo = login_attempts_repository
    
    def register(self, dto: RegisterDTO, audit_context: Dict) -> AuthResponseDTO:
        """
        Registra un nuevo usuario
        Equivalente a register() en Node.js
        """
        # Verificar si el email ya existe
        existing_user = self.user_repo.find_by_email(dto.email)
        
        if existing_user:
            raise AppError.conflict('Email ya registrado')
        
        # Crear usuario (el password se hashea automáticamente en el model)
        user = self.user_repo.create({
            'email': dto.email,
            'password': dto.password,
            'name': dto.name,
            'role': dto.role
        })
        
        # Generar tokens
        tokens = jwt_util.generate_token_pair(user)
        
        logger.info('User registered', user_id=user.id, email=user.email)
        
        return AuthResponseDTO.from_data(user, tokens)
    
    def login(self, dto: LoginDTO, audit_context: Dict) -> AuthResponseDTO:
        """
        Login de usuario
        Equivalente a login() en Node.js
        """
        ip_address = audit_context.get('ip', 'unknown')
        
        # Verificar si está bloqueado
        if self.login_attempts_repo.is_blocked(dto.email):
            remaining = self.login_attempts_repo.get_remaining_block_time(dto.email)
            minutes = remaining // 60
            raise AppError.too_many_requests(
                f'Cuenta bloqueada por {minutes} minutos debido a múltiples intentos fallidos'
            )
        
        # Buscar usuario activo
        user = self.user_repo.find_active_by_email(dto.email)
        
        if not user:
            # Incrementar intentos
            self.login_attempts_repo.increment_attempts(dto.email, ip_address)
            raise AppError.unauthorized('Credenciales inválidas')
        
        # Verificar password
        if not user.check_password(dto.password):
            # Incrementar intentos
            self.login_attempts_repo.increment_attempts(dto.email, ip_address)
            raise AppError.unauthorized('Credenciales inválidas')
        
        # Resetear intentos
        self.login_attempts_repo.reset_attempts(dto.email)
        
        # Actualizar last_login
        self.user_repo.update_last_login(user.id)
        
        # Generar tokens
        tokens = jwt_util.generate_token_pair(user)
        
        logger.info('User logged in', user_id=user.id, email=user.email)
        
        return AuthResponseDTO.from_data(user, tokens)
    
    def logout(self, user_id: str, token: str, audit_context: Dict) -> Dict:
        """
        Logout de usuario
        Equivalente a logout() en Node.js
        
        Note: En Flask no hay blacklist de tokens por defecto.
        Deberías implementarlo con Redis si lo necesitas.
        """
        logger.info('User logged out', user_id=user_id)
        
        return {'message': 'Logout exitoso'}
    
    def refresh_token(self, dto: RefreshTokenDTO, audit_context: Dict) -> AuthResponseDTO:
        """
        Refresca el access token
        Equivalente a refreshToken() en Node.js
        """
        try:
            # Verificar refresh token
            payload = jwt_util.verify_refresh_token(dto.refresh_token)
            user_id = payload.get('id')
            
            # Buscar usuario
            user = self.user_repo.find_by_id(user_id)
            
            if not user:
                raise AppError.unauthorized('Usuario no encontrado')
            
            if not user.is_active:
                raise AppError.unauthorized('Usuario inactivo')
            
            # Generar nuevos tokens
            tokens = jwt_util.generate_token_pair(user)
            
            logger.info('Token refreshed', user_id=user.id)
            
            return AuthResponseDTO.from_data(user, tokens)
            
        except pyjwt.ExpiredSignatureError:
            raise AppError.unauthorized('Refresh token expirado')
        except pyjwt.InvalidTokenError:
            raise AppError.unauthorized('Refresh token inválido')
    
    def verify_token(self, token: str) -> Dict:
        """
        Verifica un token
        Equivalente a verifyToken() en Node.js
        """
        try:
            payload = jwt_util.verify_access_token(token)
            user_id = payload.get('id')
            
            user = self.user_repo.find_by_id(user_id)
            
            if not user or not user.is_active:
                return {
                    'valid': False,
                    'reason': 'User not found or inactive'
                }
            
            return {
                'valid': True,
                'user': user.to_dict()
            }
            
        except pyjwt.ExpiredSignatureError:
            return {
                'valid': False,
                'reason': 'Token expired'
            }
        except pyjwt.InvalidTokenError as e:
            return {
                'valid': False,
                'reason': f'Invalid token: {str(e)}'
            }


# Singleton instance
auth_service = AuthService()
