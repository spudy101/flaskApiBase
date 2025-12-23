"""
Tests de integración para UserService
Se usa base de datos real (SQLite en memoria) para verificar queries y transacciones
"""

import pytest
from src.services.user_service import UserService
from src.models.user import User


@pytest.mark.integration
class TestUserServiceIntegration:
    """Tests de integración para UserService con DB real"""
    
    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.user_service = UserService()
    
    
    # ==================== TESTS DE LIST_USERS ====================
    
    def test_list_users_returns_paginated_results(self, session, create_user):
        """
        Test: Listar usuarios retorna resultados paginados
        """
        # Arrange - crear varios usuarios
        for i in range(5):
            create_user(email=f'user{i}@example.com', name=f'User {i}')
        
        # Act
        result = self.user_service.list_users({'page': 1, 'limit': 3})
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['users']) == 3
        assert result['data']['pagination']['total'] >= 5
        assert result['data']['pagination']['totalPages'] >= 2
    
    
    def test_list_users_filter_by_role(self, session, create_user):
        """
        Test: Filtrar usuarios por rol
        """
        # Arrange
        create_user(email='admin1@example.com', role='admin')
        create_user(email='admin2@example.com', role='admin')
        create_user(email='user1@example.com', role='user')
        
        # Act
        result = self.user_service.list_users({'role': 'admin'})
        
        # Assert
        assert result['success'] is True
        assert all(u['role'] == 'admin' for u in result['data']['users'])
    
    
    def test_list_users_filter_by_active_status(self, session, create_user):
        """
        Test: Filtrar usuarios por estado activo
        """
        # Arrange
        create_user(email='active@example.com', is_active=True)
        create_user(email='inactive@example.com', is_active=False)
        
        # Act
        result = self.user_service.list_users({'isActive': 'true'})
        
        # Assert
        assert result['success'] is True
        assert all(u['is_active'] is True for u in result['data']['users'])
    
    
    def test_list_users_search_by_name(self, session, create_user):
        """
        Test: Buscar usuarios por nombre
        """
        # Arrange
        create_user(email='john1@example.com', name='John Doe')
        create_user(email='john2@example.com', name='John Smith')
        create_user(email='jane@example.com', name='Jane Doe')
        
        # Act
        result = self.user_service.list_users({'search': 'John'})
        
        # Assert
        assert result['success'] is True
        assert all('John' in u['name'] for u in result['data']['users'])
    
    
    def test_list_users_search_by_email(self, session, create_user):
        """
        Test: Buscar usuarios por email
        """
        # Arrange
        create_user(email='test123@example.com')
        create_user(email='other@example.com')
        
        # Act
        result = self.user_service.list_users({'search': 'test123'})
        
        # Assert
        assert result['success'] is True
        assert any('test123' in u['email'] for u in result['data']['users'])
    
    
    # ==================== TESTS DE GET_USER_BY_ID ====================
    
    def test_get_user_by_id_returns_user(self, session, test_user):
        """
        Test: Obtener usuario por ID retorna datos correctos
        """
        # Act
        result = self.user_service.get_user_by_id(test_user.id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['id'] == test_user.id
        assert result['data']['email'] == test_user.email
        assert 'password' not in result['data']  # No debe incluir password
    
    
    def test_get_user_by_id_not_found(self, session):
        """
        Test: Obtener usuario inexistente falla
        """
        # Act
        result = self.user_service.get_user_by_id(99999)
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE GET_USER_BY_EMAIL ====================
    
    def test_get_user_by_email_returns_user(self, session, test_user):
        """
        Test: Obtener usuario por email retorna datos correctos
        """
        # Act
        result = self.user_service.get_user_by_email(test_user.email)
        
        # Assert
        assert result['success'] is True
        assert result['data']['email'] == test_user.email
        assert 'password' not in result['data']
    
    
    def test_get_user_by_email_not_found(self, session):
        """
        Test: Obtener usuario inexistente por email falla
        """
        # Act
        result = self.user_service.get_user_by_email('nonexistent@example.com')
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE UPDATE_USER_ROLE ====================
    
    def test_update_user_role_changes_role(self, session, test_user):
        """
        Test: Actualizar rol de usuario modifica la base de datos
        """
        # Arrange
        original_role = test_user.role
        new_role = 'admin' if original_role == 'user' else 'user'
        
        # Act
        result = self.user_service.update_user_role(test_user.id, new_role)
        
        # Assert
        assert result['success'] is True
        session.refresh(test_user)
        assert test_user.role == new_role
        assert test_user.role != original_role
    
    
    def test_update_user_role_user_not_found(self, session):
        """
        Test: Actualizar rol de usuario inexistente falla
        """
        # Act
        result = self.user_service.update_user_role(99999, 'admin')
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE DELETE_USER ====================
    
    def test_delete_user_removes_from_database(self, session, test_user):
        """
        Test: Delete elimina usuario de la base de datos (hard delete)
        """
        # Arrange
        user_id = test_user.id
        
        # Act
        result = self.user_service.delete_user(user_id)
        
        # Assert
        assert result['success'] is True
        # El usuario ya no existe en DB
        assert session.query(User).get(user_id) is None
    
    
    def test_delete_user_not_found(self, session):
        """
        Test: Eliminar usuario inexistente falla
        """
        # Act
        result = self.user_service.delete_user(99999)
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE GET_USER_STATS ====================
    
    def test_get_user_stats_calculates_correctly(self, session, create_user):
        """
        Test: Estadísticas de usuarios se calculan correctamente
        """
        # Arrange
        create_user(email='admin1@example.com', role='admin', is_active=True)
        create_user(email='admin2@example.com', role='admin', is_active=True)
        create_user(email='user1@example.com', role='user', is_active=True)
        create_user(email='user2@example.com', role='user', is_active=False)
        
        # Act
        result = self.user_service.get_user_stats()
        
        # Assert
        assert result['success'] is True
        stats = result['data']
        assert stats['total'] >= 4
        assert stats['admins'] >= 2
        assert stats['active'] >= 3
        assert stats['inactive'] >= 1
    
    
    def test_get_user_stats_with_empty_database(self, session):
        """
        Test: Estadísticas con base de datos vacía
        """
        # Act
        result = self.user_service.get_user_stats()
        
        # Assert
        assert result['success'] is True
        stats = result['data']
        assert isinstance(stats['total'], int)
        assert stats['total'] >= 0