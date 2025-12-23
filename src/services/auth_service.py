"""
Service de autenticación
Equivalente a authService.js
"""

from datetime import datetime, timedelta
from src.models.user import User
from src.models import LoginAttempt
from config.database import db
from src.utils import execute_with_transaction, execute_query, generate_token, logger


class AuthService:
    """Service de autenticación"""
    
    def register(self, user_data):
        """Registrar nuevo usuario"""
        
        def business_logic(data, session, db_instance):
            # Crear usuario (el hook beforeCreate hasheará la password)
            user = User(
                email=data['email'],
                password=data['password'],
                name=data['name'],
                role=data.get('role', 'user')
            )
            session.add(user)
            session.flush()  # Para obtener el ID
            
            logger.info('Usuario registrado exitosamente', extra={
                'userId': user.id,
                'email': user.email
            })
            
            # Generar token
            token = generate_token({
                'id': user.id,
                'email': user.email,
                'role': user.role
            })
            
            # Retornar usuario sin password
            user_dict = user.to_dict()
            
            return {
                'user': user_dict,
                'token': token
            }
        
        return execute_with_transaction(
            user_data,
            business_logic,
            'registerUser',
            {'db': db}
        )
    
    
    def login(self, email, password):
        """Login de usuario"""
        
        def query_logic(db_instance):
            # Verificar intentos de login
            login_attempt = LoginAttempt.query.filter_by(email=email).first()
            
            if login_attempt and login_attempt.blocked_until:
                if datetime.utcnow() < login_attempt.blocked_until:
                    time_left = int((login_attempt.blocked_until - datetime.utcnow()).total_seconds() / 60)
                    raise Exception(f'Cuenta bloqueada temporalmente. Intenta nuevamente en {time_left} minutos.')
            
            # Buscar usuario por email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Registrar intento fallido
                self.handle_failed_attempt(email, login_attempt)
                logger.warning('Intento de login con email no registrado', extra={'email': email})
                raise Exception('Credenciales inválidas')
            
            # Verificar si está activo
            if not user.is_active:
                logger.warning('Intento de login con usuario inactivo', extra={
                    'userId': user.id,
                    'email': email
                })
                raise Exception('Usuario inactivo')
            
            # Verificar contraseña
            is_password_valid = user.compare_password(password)
            
            if not is_password_valid:
                self.handle_failed_attempt(email, login_attempt)
                logger.warning('Intento de login con contraseña incorrecta', extra={
                    'userId': user.id,
                    'email': email
                })
                raise Exception('Credenciales inválidas')
            
            # Login exitoso: resetear intentos
            if login_attempt:
                login_attempt.attempts = 0
                login_attempt.blocked_until = None
                db_instance.session.add(login_attempt)
                db_instance.session.commit()
            
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db_instance.session.add(user)
            db_instance.session.commit()
            
            logger.info('Usuario inició sesión exitosamente', extra={
                'userId': user.id,
                'email': email
            })
            
            # Generar token
            token = generate_token({
                'id': user.id,
                'email': user.email,
                'role': user.role
            })
            
            # Retornar usuario sin password
            user_dict = user.to_dict()
            
            return {
                'user': user_dict,
                'token': token
            }
        
        return execute_query(query_logic, 'loginUser', db)
    
    
    def get_profile(self, user_id):
        """Obtener perfil de usuario"""
        
        def query_logic(db_instance):
            user = User.query.get(user_id)
            
            if not user:
                raise Exception('Usuario no encontrado')
            
            logger.debug('Perfil obtenido', extra={'userId': user_id})
            
            return user.to_dict()
        
        return execute_query(query_logic, 'getProfile', db)
    
    
    def update_profile(self, user_id, update_data):
        """Actualizar perfil de usuario"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            # Actualizar campos permitidos
            if data.get('name'):
                user.name = data['name']
            if data.get('email'):
                user.email = data['email']
            
            session.add(user)
            session.flush()
            
            logger.info('Perfil actualizado', extra={
                'userId': user.id,
                'email': user.email
            })
            
            return user.to_dict()
        
        return execute_with_transaction(
            {'userId': user_id, **update_data},
            business_logic,
            'updateProfile',
            {'db': db}
        )
    
    
    def change_password(self, user_id, current_password, new_password):
        """Cambiar contraseña"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            # Verificar contraseña actual
            is_current_password_valid = user.compare_password(data['currentPassword'])
            
            if not is_current_password_valid:
                logger.warning('Intento de cambio de contraseña con contraseña actual incorrecta', extra={
                    'userId': user.id
                })
                
                return {
                    '_rollback': True,
                    'message': 'La contraseña actual es incorrecta',
                    'data': None
                }
            
            # Actualizar contraseña (el hook beforeUpdate hasheará la nueva password)
            user.password = data['newPassword']
            session.add(user)
            session.flush()
            
            logger.info('Contraseña cambiada exitosamente', extra={'userId': user.id})
            
            return {'message': 'Contraseña actualizada exitosamente'}
        
        return execute_with_transaction(
            {'userId': user_id, 'currentPassword': current_password, 'newPassword': new_password},
            business_logic,
            'changePassword',
            {'db': db}
        )
    
    
    def deactivate_user(self, user_id):
        """Desactivar usuario (soft delete)"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            user.is_active = False
            session.add(user)
            session.flush()
            
            logger.info('Usuario desactivado', extra={'userId': user.id})
            
            return {'message': 'Usuario desactivado exitosamente'}
        
        return execute_with_transaction(
            {'userId': user_id},
            business_logic,
            'deactivateUser',
            {'db': db}
        )
    
    
    def activate_user(self, user_id):
        """Activar usuario"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            user.is_active = True
            session.add(user)
            session.flush()
            
            logger.info('Usuario activado', extra={'userId': user.id})
            
            return {'message': 'Usuario activado exitosamente'}
        
        return execute_with_transaction(
            {'userId': user_id},
            business_logic,
            'activateUser',
            {'db': db}
        )
    
    
    def handle_failed_attempt(self, email, login_attempt):
        """Manejar intento fallido"""
        MAX_ATTEMPTS = 5
        BLOCK_DURATION_MINUTES = 15
        print("***********************************************************************")
        print("***********************************************************************")
        print("***********************************************************************")
        print("***********************************************************************")
        print(login_attempt)
        print("***********************************************************************")
        print("***********************************************************************")
        print("***********************************************************************")
        print("***********************************************************************")
        if not login_attempt:
            print("***********************************************************************")
            print("***********************************************************************")
            print("***********************************************************************")
            print("***********************************************************************")
            print(login_attempt)
            print("***********************************************************************")
            print("***********************************************************************")
            print("***********************************************************************")
            print("***********************************************************************")
            login_attempt = LoginAttempt(
                email=email,
                attempts=1,
                ip_address=None  # Podría pasarse si se modifica la firma
            )
            db.session.add(login_attempt)
        else:
            login_attempt.attempts += 1
            
            if login_attempt.attempts >= MAX_ATTEMPTS:
                login_attempt.blocked_until = datetime.utcnow() + timedelta(minutes=BLOCK_DURATION_MINUTES)
            
            db.session.add(login_attempt)
        
        db.session.commit()


# Exportar instancia única
auth_service = AuthService()