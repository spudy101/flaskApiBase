from flask import request
from src.utils import validation_error_response, logger
from functools import wraps
from marshmallow import ValidationError

def validate_request(validation_func):
    """
    Middleware para validar requests
    validation_func debe lanzar ValidationError si falla
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            print("🔥 JSON QUE LLEGA AL SCHEMA:", repr(data))

            if not isinstance(data, dict):
                return validation_error_response({
                    '_schema': ['Body JSON inválido o vacío']
                })

            try:
                # 🔥 VALIDAR UNA SOLA VEZ
                validation_func(data)
            except ValidationError as err:
                logger.warning(
                    'Errores de validación',
                    extra={
                        'errors': err.messages,
                        'url': request.url,
                        'method': request.method,
                        'userId': getattr(getattr(request, 'user', None), 'id', None)
                    }
                )
                return validation_error_response(err.messages)

            # ✅ Si llega aquí, la data es válida
            return func(*args, **kwargs)

        return wrapper
    return decorator
