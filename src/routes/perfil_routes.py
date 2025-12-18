from flask import Blueprint
from src.controllers.perfil_controller import get_datos_usuario_handler
from src.middlewares.auth_middleware import verificar_autenticacion, verificar_timestamp
from src.middlewares.request_lock_middleware import with_request_lock

# Crear Blueprint (equivalente a express.Router())
perfil_bp = Blueprint('perfil_usuario', __name__, url_prefix='/perfil_usuario')

@perfil_bp.route('/datos_usuario', methods=['GET'])
@verificar_timestamp
@verificar_autenticacion
@with_request_lock(lambda: getattr(request, 'usuario', {}).get('party_uuid'))
def get_datos_usuario():
    """
    Endpoint para obtener datos del usuario autenticado
    ---
    tags:
      - perfil_usuario
    parameters:
      - in: header
        name: timestamp
        required: true
        schema:
          type: string
        description: Timestamp encriptado, para validar que el response sea reciente.
      - in: cookie
        name: jwtToken
        required: true
        schema:
          type: string
        description: Token JWT en cookie.
    responses:
      200:
        description: Datos del usuario obtenidos correctamente.
        schema:
          type: object
          properties:
            data:
              type: object
            message:
              type: string
            estado_solicitud:
              type: integer
      210:
        description: Token no válido.
      500:
        description: Error interno del servidor.
    """
    return get_datos_usuario_handler()

__all__ = ['perfil_bp']
