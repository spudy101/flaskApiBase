import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union
import jwt
from src.utils.logger import logger

# Configuración desde variables de entorno
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '24h')  # Default 24 horas
JWT_ALGORITHM = 'HS256'

if not JWT_SECRET:
    raise ValueError('JWT_SECRET no está definido en las variables de entorno')


def _parse_expiration(expires_in: str) -> timedelta:
    """
    Convierte string de tiempo (ej: '24h', '7d', '30m') a timedelta
    
    Args:
        expires_in: String con formato '24h', '7d', '30m', '60s'
        
    Returns:
        timedelta object
    """
    unit = expires_in[-1]
    value = int(expires_in[:-1])
    
    if unit == 's':  # segundos
        return timedelta(seconds=value)
    elif unit == 'm':  # minutos
        return timedelta(minutes=value)
    elif unit == 'h':  # horas
        return timedelta(hours=value)
    elif unit == 'd':  # días
        return timedelta(days=value)
    else:
        raise ValueError(f'Formato de expiración inválido: {expires_in}')


def generate_token(payload: Dict, expires_in: str = None) -> str:
    """
    Genera un token JWT
    
    Args:
        payload: Datos a incluir en el token (debe tener: id, email, role)
        expires_in: Tiempo de expiración (opcional, ej: '24h', '7d')
        
    Returns:
        Token JWT string
        
    Raises:
        Exception: Si hay error al generar el token
    """
    try:
        # Solo incluir datos mínimos necesarios
        token_payload = {
            'id': payload.get('id'),
            'email': payload.get('email'),
            'role': payload.get('role'),
            'iat': datetime.utcnow(),
            'iss': 'your-app-name',  # Cambia esto por el nombre de tu app
            'aud': 'your-app-users'
        }
        
        # Calcular expiración
        exp_time = expires_in or JWT_EXPIRES_IN
        expiration_delta = _parse_expiration(exp_time)
        token_payload['exp'] = datetime.utcnow() + expiration_delta
        
        # Generar token
        token = jwt.encode(
            token_payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        logger.debug(f'Token generado exitosamente para user_id: {payload.get("id")}')
        return token
        
    except Exception as error:
        logger.error(f'Error al generar token: {str(error)}')
        raise Exception('Error al generar token de autenticación')


def verify_token(token: str) -> Dict:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Payload decodificado
        
    Raises:
        Exception: Si el token es inválido o expiró
    """
    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer='your-app-name',
            audience='your-app-users'
        )
        
        logger.debug(f'Token verificado exitosamente para user_id: {decoded.get("id")}')
        return decoded
        
    except jwt.ExpiredSignatureError as error:
        logger.warning(f'Token expirado: {str(error)}')
        raise Exception('Token expirado')
        
    except jwt.InvalidTokenError as error:
        logger.warning(f'Token inválido: {str(error)}')
        raise Exception('Token inválido')
        
    except Exception as error:
        logger.error(f'Error al verificar token: {str(error)}')
        raise Exception('Error al verificar token')


def decode_token(token: str) -> Optional[Dict]:
    """
    Decodifica un token sin verificar (útil para debugging)
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload decodificado o None si hay error
    """
    try:
        # Decodificar sin verificar firma
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return decoded
        
    except Exception as error:
        logger.error(f'Error al decodificar token: {str(error)}')
        return None


def generate_refresh_token(payload: Dict) -> str:
    """
    Genera un refresh token (token de larga duración)
    
    Args:
        payload: Datos a incluir en el token
        
    Returns:
        Refresh token (válido por 7 días)
    """
    return generate_token(payload, expires_in='7d')


def extract_token_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extrae el token JWT del header Authorization
    
    Args:
        authorization_header: Header 'Authorization' (formato: 'Bearer <token>')
        
    Returns:
        Token JWT o None si no es válido
    """
    if not authorization_header:
        return None
    
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Obtiene la fecha de expiración de un token
    
    Args:
        token: Token JWT
        
    Returns:
        datetime de expiración o None si no se puede obtener
    """
    try:
        decoded = decode_token(token)
        if decoded and 'exp' in decoded:
            return datetime.fromtimestamp(decoded['exp'])
        return None
        
    except Exception:
        return None


def is_token_expired(token: str) -> bool:
    """
    Verifica si un token está expirado sin lanzar excepción
    
    Args:
        token: Token JWT
        
    Returns:
        True si está expirado, False si no
    """
    try:
        verify_token(token)
        return False
    except Exception as error:
        if 'expirado' in str(error).lower():
            return True
        return False