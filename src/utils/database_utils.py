"""
Utilidades de base de datos con transacciones y manejo de errores
Equivalente a src/utils/databaseUtils.js
"""
import time
from datetime import datetime
from typing import Any, Callable, Dict
from src.database.connection import db

def execute_with_transaction(
    input_data: Dict[str, Any],
    business_logic: Callable,
    operation_name: str
) -> Dict[str, Any]:
    """
    Estructura estándar para servicios con transacciones y rollback automático
    Equivalente a executeWithTransaction() de Node.js
    
    Args:
        input_data: Datos de entrada
        business_logic: Función con la lógica de negocio a ejecutar
        operation_name: Nombre de la operación para logs
        
    Returns:
        Dict con resultado estandarizado
    """
    start_time = time.time()
    
    try:
        print(f"[{operation_name}] Iniciando operación", {
            'timestamp': datetime.now().isoformat(),
            'input': input_data
        })
        
        # Ejecutar lógica de negocio dentro de la transacción
        result = business_logic(input_data)
        
        # Commit si todo sale bien
        db.session.commit()
        
        execution_time = (time.time() - start_time) * 1000
        print(f"[{operation_name}] Operación completada exitosamente", {
            'timestamp': datetime.now().isoformat(),
            'executionTime': f"{execution_time:.2f}ms",
            'result': result
        })
        
        return {
            'success': True,
            'data': result,
            'message': f'{operation_name} completada exitosamente',
            'executionTime': execution_time
        }
        
    except Exception as error:
        # Rollback automático en caso de error
        db.session.rollback()
        
        execution_time = (time.time() - start_time) * 1000
        print(f"[{operation_name}] Error en operación", {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'input': input_data,
            'executionTime': f"{execution_time:.2f}ms"
        })
        
        return {
            'success': False,
            'data': None,
            'message': str(error) or f'Error en {operation_name}',
            'errorCode': getattr(error, 'code', 'INTERNAL_ERROR'),
            'executionTime': execution_time
        }

def execute_query(
    query_params: Dict[str, Any],
    query_logic: Callable,
    query_name: str
) -> Dict[str, Any]:
    """
    Estructura estándar para consultas de solo lectura (SELECT)
    Equivalente a executeQuery() de Node.js
    
    Args:
        query_params: Parámetros de la consulta
        query_logic: Función con la lógica de consulta a ejecutar
        query_name: Nombre de la consulta para logs
        
    Returns:
        Dict con resultado estandarizado
    """
    start_time = time.time()
    
    try:
        print(f"[{query_name}] Iniciando consulta", {
            'timestamp': datetime.now().isoformat(),
            'params': query_params
        })
        
        # Ejecutar lógica de consulta (sin transacción)
        result = query_logic(query_params)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Calcular count
        if isinstance(result, list):
            result_count = len(result)
        elif result is not None:
            result_count = 1
        else:
            result_count = 0
        
        print(f"[{query_name}] Consulta completada exitosamente", {
            'timestamp': datetime.now().isoformat(),
            'executionTime': f"{execution_time:.2f}ms",
            'resultCount': result_count,
            'hasData': bool(result)
        })
        
        return {
            'success': True,
            'data': result,
            'message': f'{query_name} completada exitosamente',
            'count': result_count,
            'executionTime': execution_time
        }
        
    except Exception as error:
        execution_time = (time.time() - start_time) * 1000
        print(f"[{query_name}] Error en consulta", {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'params': query_params,
            'executionTime': f"{execution_time:.2f}ms"
        })
        
        return {
            'success': False,
            'data': None,
            'message': str(error) or f'Error en {query_name}',
            'errorCode': getattr(error, 'code', 'QUERY_ERROR'),
            'count': 0,
            'executionTime': execution_time
        }

def validate_connection() -> bool:
    """
    Valida que la conexión a la base de datos esté activa
    Equivalente a validateConnection() de Node.js
    
    Returns:
        bool: True si la conexión está activa
    """
    try:
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        return True
    except Exception as error:
        print(f"❌ Error de conexión a BD: {str(error)}")
        return False

def get_pool_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del pool de conexiones
    Equivalente a getPoolStats() de Node.js
    
    Returns:
        Dict con estadísticas del pool
    """
    try:
        pool = db.engine.pool
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow()
        }
    except Exception:
        return {'message': 'Pool no disponible'}

__all__ = [
    'execute_with_transaction',
    'execute_query',
    'validate_connection',
    'get_pool_stats'
]
