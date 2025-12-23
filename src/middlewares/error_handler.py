# middlewares/error_handler.py
from flask import jsonify, request
from src.utils import error_response, logger
from sqlalchemy.exc import IntegrityError, DataError

def error_handler(error):
    """
    Middleware para manejar errores de forma centralizada
    """

    # 🔥 LOG COMPLETO CON STACKTRACE
    logger.exception(
        '🔥 Error capturado por errorHandler',
        extra={
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr,
            'userId': getattr(getattr(request, 'user', None), 'id', None)
        }
    )

    # ----------------------------
    # ERRORES DE BASE DE DATOS
    # ----------------------------
    if isinstance(error, IntegrityError):
        msg = str(error).lower()
        if 'unique' in msg or 'duplicate' in msg:
            return error_response('El campo ya existe', 409)
        if 'foreign key' in msg:
            return error_response('Referencia inválida a otro registro', 400)
        return error_response('Error de integridad en la base de datos', 400)

    if isinstance(error, DataError):
        return error_response('Error en la base de datos', 500)

    # ----------------------------
    # ERRORES DE AUTENTICACIÓN
    # ----------------------------
    error_message = str(error)

    if error_message == 'Token expirado':
        return error_response('Tu sesión ha expirado', 401)

    if error_message == 'Token inválido':
        return error_response('Token de autenticación inválido', 401)

    if error_message == 'UnauthorizedError':
        return error_response('No autorizado', 401)

    # ----------------------------
    # ERRORES PERSONALIZADOS
    # ----------------------------
    if hasattr(error, 'code') and error.code == 400 and hasattr(error, 'errors'):
        return error_response(str(error), 400, error.errors)

    if hasattr(error, 'code') and error.code in ['TRANSACTION_ERROR', 'QUERY_ERROR']:
        return error_response(
            str(error) or 'Error en la operación de base de datos',
            500
        )

    if hasattr(error, 'code') and error.code == 404:
        return error_response(
            str(error) or 'Recurso no encontrado',
            404
        )

    # ----------------------------
    # ERROR GENÉRICO
    # ----------------------------
    status_code = getattr(error, 'code', 500)
    message = str(error) or 'Error interno del servidor'

    return error_response(message, status_code)


def not_found_handler(error):
    """
    Middleware para manejar rutas no encontradas (404)
    """
    logger.warning('Ruta no encontrada', extra={
        'url': request.url,
        'method': request.method,
        'ip': request.remote_addr
    })
    
    return error_response(f'Ruta {request.path} no encontrada', 404)