"""
Tests unitarios para database_utils
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.utils.database_utils import execute_query, execute_with_transaction

class TestDatabaseUtils:
    """Tests para utilidades de base de datos"""
    
    class TestExecuteQuery:
        """Tests para execute_query"""
        
        def test_ejecuta_query_exitosamente(self):
            """Debería ejecutar query exitosamente"""
            query_params = {'id': 1}
            mock_result = {'id': 1, 'name': 'Test'}
            
            def query_logic(params):
                return mock_result
            
            result = execute_query(query_params, query_logic, 'TEST_QUERY')
            
            assert result['success'] is True
            assert result['data'] == mock_result
            assert result['count'] == 1
            assert 'executionTime' in result
        
        def test_maneja_errores_correctamente(self):
            """Debería manejar errores correctamente"""
            query_params = {'id': 1}
            
            def query_logic(params):
                raise Exception('Database error')
            
            result = execute_query(query_params, query_logic, 'TEST_QUERY')
            
            assert result['success'] is False
            assert result['data'] is None
            assert 'Database error' in result['message']
            assert result['count'] == 0
        
        def test_cuenta_arrays_correctamente(self):
            """Debería contar arrays correctamente"""
            mock_result = [1, 2, 3, 4, 5]
            
            def query_logic(params):
                return mock_result
            
            result = execute_query({}, query_logic, 'TEST_QUERY')
            
            assert result['count'] == 5
        
        def test_cuenta_cero_para_none(self):
            """Debería contar 0 para None"""
            def query_logic(params):
                return None
            
            result = execute_query({}, query_logic, 'TEST_QUERY')
            
            assert result['count'] == 0
        
        def test_incluye_execution_time(self):
            """Debería incluir execution time"""
            import time
            
            def query_logic(params):
                time.sleep(0.05)
                return 'data'
            
            result = execute_query({}, query_logic, 'TEST_QUERY')
            
            assert result['executionTime'] > 0
            assert isinstance(result['executionTime'], float)
    
    class TestExecuteWithTransaction:
        """Tests para execute_with_transaction"""
        
        @patch('src.utils.database_utils.db')
        def test_ejecuta_transaccion_exitosamente(self, mock_db):
            """Debería ejecutar transacción exitosamente"""
            mock_session = MagicMock()
            mock_db.session = mock_session
            
            input_data = {'name': 'Test'}
            mock_result = {'id': 1, 'name': 'Test'}
            
            def business_logic(params):
                return mock_result
            
            result = execute_with_transaction(input_data, business_logic, 'TEST_OPERATION')
            
            assert result['success'] is True
            assert result['data'] == mock_result
            assert mock_session.commit.called
            assert not mock_session.rollback.called
        
        @patch('src.utils.database_utils.db')
        def test_hace_rollback_en_caso_de_error(self, mock_db):
            """Debería hacer rollback en caso de error"""
            mock_session = MagicMock()
            mock_db.session = mock_session
            
            def business_logic(params):
                raise Exception('Business logic error')
            
            result = execute_with_transaction({}, business_logic, 'TEST_OPERATION')
            
            assert result['success'] is False
            assert result['data'] is None
            assert mock_session.rollback.called
            assert not mock_session.commit.called
        
        @patch('src.utils.database_utils.db')
        def test_incluye_execution_time(self, mock_db):
            """Debería incluir execution time"""
            import time
            
            mock_session = MagicMock()
            mock_db.session = mock_session
            
            def business_logic(params):
                time.sleep(0.05)
                return 'data'
            
            result = execute_with_transaction({}, business_logic, 'TEST_OPERATION')
            
            assert result['executionTime'] > 0
            assert isinstance(result['executionTime'], float)
        
        @patch('src.utils.database_utils.db')
        def test_pasa_input_data_a_business_logic(self, mock_db):
            """Debería pasar input_data a business_logic"""
            mock_session = MagicMock()
            mock_db.session = mock_session
            
            input_data = {'test': 'data'}
            received_params = None
            
            def business_logic(params):
                nonlocal received_params
                received_params = params
                return 'result'
            
            execute_with_transaction(input_data, business_logic, 'TEST_OPERATION')
            
            assert received_params == input_data

class TestValidateConnection:
    """Tests para validate_connection"""
    
    @patch('src.utils.database_utils.db')
    def test_retorna_true_con_conexion_valida(self, mock_db):
        """Debería retornar True con conexión válida"""
        from src.utils.database_utils import validate_connection
        
        mock_session = MagicMock()
        mock_db.session = mock_session
        
        result = validate_connection()
        
        assert result is True
        assert mock_session.execute.called
    
    @patch('src.utils.database_utils.db')
    def test_retorna_false_con_error_de_conexion(self, mock_db):
        """Debería retornar False con error de conexión"""
        from src.utils.database_utils import validate_connection
        
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception('Connection error')
        mock_db.session = mock_session
        
        result = validate_connection()
        
        assert result is False

class TestGetPoolStats:
    """Tests para get_pool_stats"""
    
    @patch('src.utils.database_utils.db')
    def test_retorna_estadisticas_del_pool(self, mock_db):
        """Debería retornar estadísticas del pool"""
        from src.utils.database_utils import get_pool_stats
        
        mock_pool = MagicMock()
        mock_pool.size.return_value = 5
        mock_pool.checkedin.return_value = 3
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 0
        
        mock_db.engine.pool = mock_pool
        
        stats = get_pool_stats()
        
        assert stats['size'] == 5
        assert stats['checked_in'] == 3
        assert stats['checked_out'] == 2
        assert stats['overflow'] == 0
    
    @patch('src.utils.database_utils.db')
    def test_maneja_error_al_obtener_stats(self, mock_db):
        """Debería manejar error al obtener stats"""
        from src.utils.database_utils import get_pool_stats
        
        mock_db.engine.pool = None
        
        stats = get_pool_stats()
        
        assert 'message' in stats or 'error' in stats
