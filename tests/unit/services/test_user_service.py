"""
Tests unitarios para UserService
Se mockea la base de datos y se testea solo la lógica de negocio
"""

import pytest
from unittest.mock import Mock, patch

from src.services.user_service import UserService


@pytest.mark.unit
class TestUserServiceUnit:
    """Tests unitarios para UserService con mocks"""
    
    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.user_service = UserService()
    
    
    # ==================== TESTS DE LIST_USERS ====================
    
    @patch('src.services.user_service.execute_query')
    def test_list_users_with_pagination(self, mock_execute_query):
        """
        Test: Listar usuarios con paginación
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'users': [
                    {'id': 1, 'email': 'user1@example.com'},
                    {'id': 2, 'email': 'user2@example.com'}
                ],
                'pagination': {
                    'total': 10,
                    'page': 1,
                    'limit': 2,
                    'totalPages': 5
                }
            }
        }
        
        filters = {'page': 1, 'limit': 2}
        
        # Act
        result = self.user_service.list_users(filters)
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['users']) == 2
        assert result['data']['pagination']['total'] == 10
    
    
    @patch('src.services.user_service.execute_query')
    def test_list_users_filter_by_role(self, mock_execute_query):
        """
        Test: Filtrar usuarios por rol
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'users': [{'id': 1, 'role': 'admin'}],
                'pagination': {'total': 1, 'page': 1, 'limit': 10, 'totalPages': 1}
            }
        }
        
        # Act
        result = self.user_service.list_users({'role': 'admin'})
        
        # Assert
        assert result['success'] is True
        mock_execute_query.assert_called_once()
    
    
    @patch('src.services.user_service.execute_query')
    def test_list_users_filter_by_active_status(self, mock_execute_query):
        """
        Test: Filtrar usuarios por estado activo
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'users': [{'id': 1, 'is_active': True}],
                'pagination': {'total': 1, 'page': 1, 'limit': 10, 'totalPages': 1}
            }
        }
        
        # Act
        result = self.user_service.list_users({'isActive': 'true'})
        
        # Assert
        assert result['success'] is True
    
    
    @patch('src.services.user_service.execute_query')
    def test_list_users_search_by_name_or_email(self, mock_execute_query):
        """
        Test: Buscar usuarios por nombre o email
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'users': [{'id': 1, 'email': 'john@example.com', 'name': 'John'}],
                'pagination': {'total': 1, 'page': 1, 'limit': 10, 'totalPages': 1}
            }
        }
        
        # Act
        result = self.user_service.list_users({'search': 'john'})
        
        # Assert
        assert result['success'] is True
    
    
    # ==================== TESTS DE GET_USER_BY_ID ====================
    
    @patch('src.services.user_service.execute_query')
    def test_get_user_by_id_success(self, mock_execute_query):
        """
        Test: Obtener usuario por ID exitosamente
        """
        # Arrange
        user_id = 1
        mock_execute_query.return_value = {
            'success': True,
            'data': {'id': user_id, 'email': 'test@example.com'}
        }
        
        # Act
        result = self.user_service.get_user_by_id(user_id)
        
        # Assert
        assert result['success'] is True
        assert result['data']['id'] == user_id
    
    
    @patch('src.services.user_service.execute_query')
    def test_get_user_by_id_not_found(self, mock_execute_query):
        """
        Test: Usuario no encontrado
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Usuario no encontrado'
        }
        
        # Act
        result = self.user_service.get_user_by_id(999)
        
        # Assert
        assert result['success'] is False
        assert 'no encontrado' in result['message'].lower()
    
    
    # ==================== TESTS DE GET_USER_BY_EMAIL ====================
    
    @patch('src.services.user_service.execute_query')
    def test_get_user_by_email_success(self, mock_execute_query):
        """
        Test: Obtener usuario por email exitosamente
        """
        # Arrange
        email = 'test@example.com'
        mock_execute_query.return_value = {
            'success': True,
            'data': {'id': 1, 'email': email}
        }
        
        # Act
        result = self.user_service.get_user_by_email(email)
        
        # Assert
        assert result['success'] is True
        assert result['data']['email'] == email
    
    
    @patch('src.services.user_service.execute_query')
    def test_get_user_by_email_not_found(self, mock_execute_query):
        """
        Test: Usuario no encontrado por email
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': False,
            'message': 'Usuario no encontrado'
        }
        
        # Act
        result = self.user_service.get_user_by_email('nonexistent@example.com')
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE UPDATE_USER_ROLE ====================
    
    @patch('src.services.user_service.execute_with_transaction')
    def test_update_user_role_success(self, mock_execute_transaction):
        """
        Test: Actualizar rol de usuario exitosamente
        """
        # Arrange
        user_id = 1
        new_role = 'admin'
        
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'id': user_id, 'role': new_role}
        }
        
        # Act
        result = self.user_service.update_user_role(user_id, new_role)
        
        # Assert
        assert result['success'] is True
        assert result['data']['role'] == new_role
    
    
    @patch('src.services.user_service.execute_with_transaction')
    def test_update_user_role_user_not_found(self, mock_execute_transaction):
        """
        Test: Falla al actualizar rol de usuario inexistente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'Usuario no encontrado'
        }
        
        # Act
        result = self.user_service.update_user_role(999, 'admin')
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE DELETE_USER ====================
    
    @patch('src.services.user_service.execute_with_transaction')
    def test_delete_user_success(self, mock_execute_transaction):
        """
        Test: Eliminar usuario permanentemente exitosamente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': True,
            'data': {'message': 'Usuario eliminado permanentemente'}
        }
        
        # Act
        result = self.user_service.delete_user(1)
        
        # Assert
        assert result['success'] is True
    
    
    @patch('src.services.user_service.execute_with_transaction')
    def test_delete_user_not_found(self, mock_execute_transaction):
        """
        Test: Falla al eliminar usuario inexistente
        """
        # Arrange
        mock_execute_transaction.return_value = {
            'success': False,
            'message': 'Usuario no encontrado'
        }
        
        # Act
        result = self.user_service.delete_user(999)
        
        # Assert
        assert result['success'] is False
    
    
    # ==================== TESTS DE GET_USER_STATS ====================
    
    @patch('src.services.user_service.execute_query')
    def test_get_user_stats_success(self, mock_execute_query):
        """
        Test: Obtener estadísticas de usuarios
        """
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {
                'total': 100,
                'active': 80,
                'inactive': 20,
                'admins': 5,
                'users': 95
            }
        }
        
        # Act
        result = self.user_service.get_user_stats()
        
        # Assert
        assert result['success'] is True
        assert result['data']['total'] == 100
        assert result['data']['active'] == 80
        assert result['data']['admins'] == 5