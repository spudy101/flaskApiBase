# utils/response_handler.py
from flask import jsonify, current_app
from datetime import datetime
import os

def success_response(data=None, message='Operación exitosa', status_code=200):
    """
    Maneja respuestas exitosas de forma estandarizada
    
    Args:
        data: Datos a enviar
        message: Mensaje descriptivo
        status_code: Código HTTP (default: 200)
    """
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code


def error_response(message='Error en el servidor', status_code=500, errors=None):
    """
    Maneja respuestas de error de forma estandarizada
    
    Args:
        message: Mensaje de error
        status_code: Código HTTP (default: 500)
        errors: Detalles adicionales del error
    """
    response = {
        'success': False,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Solo incluir detalles de errores en desarrollo
    if current_app.debug and errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def validation_error_response(errors):
    formatted_errors = []

    if isinstance(errors, dict):
        for field, messages in errors.items():

            # 🔥 FIX CLAVE
            if isinstance(messages, str):
                messages = [messages]

            for message in messages:
                formatted_errors.append({
                    'field': field,
                    'message': message
                })

    elif isinstance(errors, list):
        for err in errors:
            if isinstance(err, dict):
                formatted_errors.append({
                    'field': err.get('path') or err.get('param'),
                    'message': err.get('msg') or err.get('message')
                })
            else:
                formatted_errors.append({
                    'field': None,
                    'message': str(err)
                })

    else:
        formatted_errors.append({
            'field': None,
            'message': str(errors)
        })

    return jsonify({
        'success': False,
        'message': 'Errores de validación',
        'errors': formatted_errors,
        'timestamp': datetime.utcnow().isoformat()
    }), 400


def paginated_response(data, page, limit, total, message='Datos obtenidos exitosamente'):
    """
    Maneja respuestas paginadas
    
    Args:
        data: Datos paginados
        page: Página actual
        limit: Límite por página
        total: Total de registros
        message: Mensaje descriptivo
    """
    import math
    total_pages = math.ceil(total / limit)
    
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'page': int(page),
            'limit': int(limit),
            'total': total,
            'totalPages': total_pages,
            'hasNextPage': page < total_pages,
            'hasPrevPage': page > 1
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 200