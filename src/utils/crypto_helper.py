import os
import hashlib
import secrets
import json
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Union, Dict, Tuple
from src.utils.logger import logger

# Configuración
ALGORITHM = 'aes-256-gcm'
KEY_LENGTH = 32  # 256 bits
IV_LENGTH = 12   # 96 bits (recomendado para GCM)
SALT_LENGTH = 64
ITERATIONS = 100000

# Obtener clave de encriptación desde variables de entorno
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    logger.warning('⚠️  ENCRYPTION_KEY no está definido en .env. Se generará una clave temporal.')


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Genera una clave derivada desde una contraseña usando PBKDF2
    
    Args:
        password: Contraseña base
        salt: Salt para derivar la clave
        
    Returns:
        Clave derivada de 32 bytes
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode())


def encrypt(data: Union[str, dict, list]) -> str:
    """
    Encripta un texto o JSON usando AES-256-GCM
    
    Args:
        data: Datos a encriptar (str, dict o list)
        
    Returns:
        String en formato: salt:iv:encryptedData (base64)
        
    Raises:
        Exception: Si hay error en la encriptación
    """
    try:
        # Convertir objeto a string si es necesario
        if isinstance(data, (dict, list)):
            text = json.dumps(data)
        else:
            text = str(data)
        
        # Generar salt e IV aleatorios
        salt = secrets.token_bytes(SALT_LENGTH)
        iv = secrets.token_bytes(IV_LENGTH)
        
        # Derivar clave desde ENCRYPTION_KEY
        key_base = ENCRYPTION_KEY or 'default-key-change-in-production'
        key = derive_key(key_base, salt)
        
        # Crear cipher con AESGCM
        aesgcm = AESGCM(key)
        
        # Encriptar (incluye authentication tag automáticamente)
        encrypted = aesgcm.encrypt(iv, text.encode('utf-8'), None)
        
        # Retornar: salt:iv:encryptedData (todo en base64)
        result = ':'.join([
            b64encode(salt).decode('utf-8'),
            b64encode(iv).decode('utf-8'),
            b64encode(encrypted).decode('utf-8')
        ])
        
        logger.debug('Datos encriptados exitosamente')
        return result
        
    except Exception as error:
        logger.error(f'Error al encriptar datos: {str(error)}')
        raise Exception('Error al encriptar datos')


def decrypt(encrypted_data: str) -> Union[str, dict, list]:
    """
    Desencripta datos previamente encriptados
    
    Args:
        encrypted_data: String en formato salt:iv:encryptedData (base64)
        
    Returns:
        Datos desencriptados (parseados como JSON si es posible)
        
    Raises:
        Exception: Si hay error en la desencriptación
    """
    try:
        # Separar componentes
        parts = encrypted_data.split(':')
        
        if len(parts) != 3:
            raise ValueError('Formato de datos encriptados inválido')
        
        salt = b64decode(parts[0])
        iv = b64decode(parts[1])
        encrypted = b64decode(parts[2])
        
        # Derivar clave
        key_base = ENCRYPTION_KEY or 'default-key-change-in-production'
        key = derive_key(key_base, salt)
        
        # Crear decipher
        aesgcm = AESGCM(key)
        
        # Desencriptar (verifica authentication tag automáticamente)
        decrypted = aesgcm.decrypt(iv, encrypted, None)
        decrypted_text = decrypted.decode('utf-8')
        
        logger.debug('Datos desencriptados exitosamente')
        
        # Intentar parsear como JSON
        try:
            return json.loads(decrypted_text)
        except json.JSONDecodeError:
            return decrypted_text
            
    except Exception as error:
        logger.error(f'Error al desencriptar datos: {str(error)}')
        raise Exception('Error al desencriptar datos')


def hash_password(data: str, salt: str = None) -> Dict[str, str]:
    """
    Hash de una sola vía para passwords (PBKDF2)
    
    Args:
        data: Datos a hashear
        salt: Salt opcional (se genera automáticamente si no se provee)
        
    Returns:
        Dict con 'hash' y 'salt'
        
    Raises:
        Exception: Si hay error al generar el hash
    """
    try:
        # Generar salt si no se provee
        salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(SALT_LENGTH)
        
        # Generar hash usando PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=KEY_LENGTH,
            salt=salt_bytes,
            iterations=ITERATIONS,
        )
        hash_bytes = kdf.derive(data.encode())
        
        logger.debug('Hash generado exitosamente')
        
        return {
            'hash': hash_bytes.hex(),
            'salt': salt_bytes.hex()
        }
        
    except Exception as error:
        logger.error(f'Error al generar hash: {str(error)}')
        raise Exception('Error al generar hash')


def verify_hash(data: str, hash_value: str, salt: str) -> bool:
    """
    Verifica un hash (para passwords)
    
    Args:
        data: Dato a verificar
        hash_value: Hash guardado
        salt: Salt usado en el hash
        
    Returns:
        True si coincide, False si no
    """
    try:
        calculated = hash_password(data, salt)
        return calculated['hash'] == hash_value
        
    except Exception as error:
        logger.error(f'Error al verificar hash: {str(error)}')
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Genera un token aleatorio seguro
    
    Args:
        length: Longitud del token en bytes (default: 32)
        
    Returns:
        Token hexadecimal
    """
    return secrets.token_hex(length)


def generate_uuid() -> str:
    """
    Genera un UUID v4
    
    Returns:
        UUID string
    """
    import uuid
    return str(uuid.uuid4())


def quick_hash(data: str) -> str:
    """
    Hash rápido para identificadores (MD5)
    
    NOTA: No usar para passwords, solo para identificadores únicos
    
    Args:
        data: Datos a hashear
        
    Returns:
        Hash MD5 hexadecimal
    """
    return hashlib.md5(data.encode()).hexdigest()


def encrypt_sensitive_data(data: Union[str, dict, list]) -> str:
    """
    Encripta datos sensibles para almacenar en BD
    Útil para: tokens de API, datos de tarjetas, etc.
    
    Args:
        data: Datos sensibles
        
    Returns:
        Datos encriptados
    """
    logger.info('Encriptando datos sensibles')
    return encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> Union[str, dict, list]:
    """
    Desencripta datos sensibles desde BD
    
    Args:
        encrypted_data: Datos encriptados
        
    Returns:
        Datos originales
    """
    logger.info('Desencriptando datos sensibles')
    return decrypt(encrypted_data)