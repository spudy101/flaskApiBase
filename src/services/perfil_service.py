import os
from src.utils.database_utils import execute_query

def get_datos_usuario(token: str):
    """
    Obtiene los datos del usuario por token
    Equivalente a getDatosUsuario() de Node.js
    
    Args:
        token: Token del usuario
        
    Returns:
        Dict con resultado de la operación
    """
    def query_logic(params):
        # IMPORTANTE: Esta es una implementación de ejemplo
        # Debes importar y usar tus modelos reales una vez los generes
        
        """
        Ejemplo con SQLAlchemy (descomentar cuando tengas los modelos):
        
        from src.models import Usuario, Persona, Avatar, Rol, PrefijoTelefonico
        
        usuario = Usuario.query.filter_by(token=params['token']).filter(
            Usuario.id_rol.in_([1, 2])
        ).join(
            Persona
        ).join(
            Avatar
        ).join(
            Rol
        ).join(
            PrefijoTelefonico, Persona.id_prefijo_telefonico == PrefijoTelefonico.id_prefijo_telefonico
        ).first()
        
        if not usuario:
            return None
        
        # Transformar a la estructura esperada
        return {
            'id_rol': usuario.id_rol,
            'id_persona': usuario.id_persona,
            'id_avatar': usuario.id_avatar,
            'id_usuario': usuario.id_usuario,
            'run': usuario.persona.run,
            'nombres': usuario.persona.nombres,
            'apellidos': usuario.persona.apellidos,
            'fecha_nacimiento': str(usuario.persona.fecha_nacimiento),
            'correo': usuario.persona.correo,
            'telefono': usuario.persona.telefono,
            'id_prefijo_telefonico': usuario.persona.id_prefijo_telefonico,
            'nombre_avatar': f"https://{os.getenv('BUCKET_NAME', 'nombreBucket')}.s3.us-east-1.amazonaws.com/avatares/{usuario.avatar.nombre_avatar}",
            'nombre_rol': usuario.rol.nombre_rol,
            'autentificador': usuario.autentificador,
            'prefijo': usuario.persona.prefijo_telefonico.prefijo
        }
        """
        
        # VERSIÓN TEMPORAL DE EJEMPLO (REEMPLAZAR CON CÓDIGO REAL)
        if params['token'] == 'test-token':
            return {
                'id_rol': 1,
                'id_persona': 1,
                'id_avatar': 1,
                'id_usuario': 1,
                'run': '12345678-9',
                'nombres': 'Usuario',
                'apellidos': 'Prueba',
                'fecha_nacimiento': '1990-01-01',
                'correo': 'usuario@test.com',
                'telefono': '987654321',
                'id_prefijo_telefonico': 1,
                'nombre_avatar': f"https://{os.getenv('BUCKET_NAME', 'nombreBucket')}.s3.us-east-1.amazonaws.com/avatares/default.png",
                'nombre_rol': 'Admin',
                'autentificador': False,
                'prefijo': '+56'
            }
        
        return None
    
    return execute_query(
        {'token': token},
        query_logic,
        'GET_DATOS_USUARIO'
    )

__all__ = ['get_datos_usuario']
