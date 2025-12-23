from flask import current_app
import time
from .logger import logger

def execute_with_transaction(input_data, business_logic, operation_name, options=None):
    """
    Ejecuta lógica de negocio dentro de una transacción con manejo robusto
    
    Args:
        input_data: Datos de entrada
        business_logic: Función (data, session, db) => result
        operation_name: Nombre de la operación para logs
        options: Opciones adicionales
            - db: Instancia de SQLAlchemy
            - log_input: Boolean para loguear datos de entrada (default: False)
    
    Returns:
        dict: { success, data, message, execution_time }
    """
    if options is None:
        options = {}
    
    db = options.get('db')
    log_input = options.get('log_input', False)
    
    if not db:
        raise ValueError('Se requiere instancia de SQLAlchemy (db)')
    
    session = db.session
    start_time = time.time()
    
    try:
        log_data = {'operation': operation_name}
        if log_input:
            log_data['input'] = input_data
        
        logger.info(f'[{operation_name}] Iniciando transacción', extra=log_data)
        
        result = business_logic(input_data, session, db)
        
        # Verificar rollback explícito
        if result and isinstance(result, dict) and result.get('_rollback'):
            session.rollback()
            
            execution_time = int((time.time() - start_time) * 1000)
            logger.warning(f'[{operation_name}] Rollback solicitado', extra={
                'execution_time': f'{execution_time}ms',
                'reason': result.get('message', 'Rollback explícito')
            })
            
            # Eliminar el flag interno antes de devolver
            del result['_rollback']
            
            return {
                'success': False,
                'data': result.get('data'),
                'message': result.get('message', f'{operation_name} requirió rollback'),
                'execution_time': execution_time
            }
        
        session.commit()
        
        execution_time = int((time.time() - start_time) * 1000)
        logger.info(f'[{operation_name}] Transacción completada', extra={
            'execution_time': f'{execution_time}ms'
        })
        
        return {
            'success': True,
            'data': result,
            'message': f'{operation_name} completada exitosamente',
            'execution_time': execution_time
        }
        
    except Exception as error:
        session.rollback()
        
        execution_time = int((time.time() - start_time) * 1000)
        
        error_data = {
            'error': str(error),
            'execution_time': f'{execution_time}ms'
        }
        
        import os
        if current_app.debug:
            import traceback
            error_data['stack'] = traceback.format_exc()
        
        logger.error(f'[{operation_name}] Error en transacción', extra=error_data)
        
        # Lanzar error para que el controller lo maneje
        raise Exception(str(error))


def execute_query(query_logic, operation_name, db):
    """
    Ejecuta consultas sin transacción (para operaciones de solo lectura)
    
    Args:
        query_logic: Función (db) => result
        operation_name: Nombre de la operación
        db: Instancia de SQLAlchemy
    
    Returns:
        dict: { success, data, message, execution_time }
    """
    if not db:
        raise ValueError('Se requiere instancia de SQLAlchemy (db)')
    
    start_time = time.time()
    
    try:
        logger.debug(f'[{operation_name}] Ejecutando consulta')
        
        result = query_logic(db)
        
        execution_time = int((time.time() - start_time) * 1000)
        logger.debug(f'[{operation_name}] Consulta completada', extra={
            'execution_time': f'{execution_time}ms'
        })
        
        return {
            'success': True,
            'data': result,
            'message': f'{operation_name} completada exitosamente',
            'execution_time': execution_time
        }
        
    except Exception as error:
        execution_time = int((time.time() - start_time) * 1000)
        
        error_data = {
            'error': str(error),
            'execution_time': f'{execution_time}ms'
        }
        
        import os
        if current_app.debug:
            import traceback
            error_data['stack'] = traceback.format_exc()
        
        logger.error(f'[{operation_name}] Error en consulta', extra=error_data)
        
        raise Exception(str(error))