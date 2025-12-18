"""
Utilidades de criptografía
Equivalente a src/utils/cryptoUtils.js
"""
import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Obtener claves de variables de entorno
AES_KEY = bytes.fromhex(os.getenv('AES_KEY', '0' * 64))  # 32 bytes en hex
AES_IV = bytes.fromhex(os.getenv('AES_IV', '0' * 32))    # 16 bytes en hex

def encriptar_mensaje(data: str) -> str:
    """
    Encripta un mensaje usando AES-256-CBC
    
    Args:
        data: Mensaje a encriptar
        
    Returns:
        str: Mensaje encriptado en hexadecimal
    """
    try:
        cipher = Cipher(
            algorithms.AES(AES_KEY),
            modes.CBC(AES_IV),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Padding PKCS7
        padding_length = 16 - (len(data) % 16)
        padded_data = data + (chr(padding_length) * padding_length)
        
        encrypted = encryptor.update(padded_data.encode('utf-8')) + encryptor.finalize()
        return encrypted.hex()
    except Exception as error:
        print(f"Error al encriptar mensaje: {str(error)}")
        raise

def desencriptar_mensaje(encrypted_data: str) -> str:
    """
    Desencripta un mensaje usando AES-256-CBC
    
    Args:
        encrypted_data: Mensaje encriptado en hexadecimal
        
    Returns:
        str: Mensaje desencriptado
    """
    try:
        cipher = Cipher(
            algorithms.AES(AES_KEY),
            modes.CBC(AES_IV),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted = decryptor.update(encrypted_bytes) + decryptor.finalize()
        
        # Remover padding PKCS7
        padding_length = decrypted[-1]
        decrypted = decrypted[:-padding_length]
        
        return decrypted.decode('utf-8')
    except Exception as error:
        print(f"Error al desencriptar mensaje: {str(error)}")
        raise

def generar_token(longitud: int = 64) -> str:
    """
    Genera un token aleatorio para sesiones
    
    Args:
        longitud: Longitud del token en bytes (default: 64)
        
    Returns:
        str: Token generado en hexadecimal
    """
    return secrets.token_hex(longitud)

__all__ = ['encriptar_mensaje', 'desencriptar_mensaje', 'generar_token']
