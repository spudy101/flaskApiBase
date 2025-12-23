"""
Service de usuarios
Equivalente a userService.js
"""

from sqlalchemy import or_
from src.models.user import User
from config.database import db
from src.utils import execute_with_transaction, execute_query, logger


class UserService:
    """Service de usuarios"""
    
    def list_users(self, filters=None):
        """Listar todos los usuarios con paginación y filtros"""
        if filters is None:
            filters = {}
        
        def query_logic(db_instance):
            page = int(filters.get('page', 1))
            limit = int(filters.get('limit', 10))
            role = filters.get('role')
            is_active = filters.get('isActive')
            search = filters.get('search')
            
            offset = (page - 1) * limit
            
            # Construir query base
            query = User.query
            
            # Aplicar filtros
            if role:
                query = query.filter(User.role == role)
            
            if is_active is not None:
                # Convertir string a boolean si es necesario
                if isinstance(is_active, str):
                    is_active = is_active.lower() == 'true'
                query = query.filter(User.is_active == is_active)
            
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_pattern),
                        User.email.ilike(search_pattern)
                    )
                )
            
            # Contar total
            total = query.count()
            
            # Aplicar paginación y ordenamiento
            users = query.order_by(
                User.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            logger.debug('Usuarios listados', extra={
                'total': total,
                'page': page,
                'limit': limit
            })
            
            return {
                'users': [user.to_dict() for user in users],
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'totalPages': (total + limit - 1) // limit
                }
            }
        
        return execute_query(query_logic, 'listUsers', db)
    
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        
        def query_logic(db_instance):
            user = User.query.get(user_id)
            
            if not user:
                raise Exception('Usuario no encontrado')
            
            logger.debug('Usuario obtenido por ID', extra={'userId': user_id})
            
            return user.to_dict()
        
        return execute_query(query_logic, 'getUserById', db)
    
    
    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        
        def query_logic(db_instance):
            user = User.query.filter_by(email=email).first()
            
            if not user:
                raise Exception('Usuario no encontrado')
            
            logger.debug('Usuario obtenido por email', extra={'email': email})
            
            return user.to_dict()
        
        return execute_query(query_logic, 'getUserByEmail', db)
    
    
    def update_user_role(self, user_id, new_role):
        """Actualizar rol de usuario (solo admin)"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            old_role = user.role
            user.role = data['newRole']
            session.add(user)
            session.flush()
            
            logger.info('Rol de usuario actualizado', extra={
                'userId': user.id,
                'oldRole': old_role,
                'newRole': data['newRole']
            })
            
            return user.to_dict()
        
        return execute_with_transaction(
            {'userId': user_id, 'newRole': new_role},
            business_logic,
            'updateUserRole',
            {'db': db}
        )
    
    
    def delete_user(self, user_id):
        """Eliminar usuario permanentemente (hard delete)"""
        
        def business_logic(data, session, db_instance):
            user = User.query.get(data['userId'])
            
            if not user:
                return {
                    '_rollback': True,
                    'message': 'Usuario no encontrado',
                    'data': None
                }
            
            session.delete(user)
            session.flush()
            
            logger.warn('Usuario eliminado permanentemente', extra={'userId': user.id})
            
            return {'message': 'Usuario eliminado permanentemente'}
        
        return execute_with_transaction(
            {'userId': user_id},
            business_logic,
            'deleteUser',
            {'db': db}
        )
    
    
    def get_user_stats(self):
        """Obtener estadísticas de usuarios"""
        
        def query_logic(db_instance):
            # Realizar consulta SQL directa para estadísticas
            result = db_instance.session.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_active = true) as active,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive,
                    COUNT(*) FILTER (WHERE role = 'admin') as admins,
                    COUNT(*) FILTER (WHERE role = 'user') as users
                FROM users
            """).fetchone()
            
            logger.debug('Estadísticas de usuarios obtenidas')
            
            # Convertir resultado a diccionario
            stats = {
                'total': int(result[0]) if result[0] else 0,
                'active': int(result[1]) if result[1] else 0,
                'inactive': int(result[2]) if result[2] else 0,
                'admins': int(result[3]) if result[3] else 0,
                'users': int(result[4]) if result[4] else 0
            }
            
            return stats
        
        return execute_query(query_logic, 'getUserStats', db)


# Exportar instancia única
user_service = UserService()