from flask import request, jsonify
from src.services.perfil_service import get_datos_usuario

def get_datos_usuario_handler():
    """
    Handler para obtener datos del usuario autenticado
    Equivalente a getDatosUsuario() de Node.js
    
    Returns:
        JSON response con los datos del usuario
    """
    try:
        # Obtener el usuario del contexto (agregado por el middleware)
        usuario = getattr(request, 'usuario', None)
        
        if not usuario:
            return jsonify({
                'message': 'Usuario no autenticado',
                'estado_solicitud': 0
            }), 401
        
        token = usuario.get('token') or usuario.get('id_usuario')
        
        # Llamar al servicio
        result = get_datos_usuario(token)
        
        if result.get('success'):
            return jsonify({
                'data': result['data'],
                'message': 'Solicitud correcta',
                'estado_solicitud': 1
            }), 200
        else:
            return jsonify({
                'message': 'Error al obtener los datos del usuario.',
                'estado_solicitud': 0
            }), 500
            
    except Exception as error:
        print(f'Error en getDatosUsuario controller: {str(error)}')
        return jsonify({
            'message': 'Error al obtener los datos del usuario.',
            'estado_solicitud': 0
        }), 500

__all__ = ['get_datos_usuario_handler']
