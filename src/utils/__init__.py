"""
Utils module - Utilidades generales para la aplicación
"""

from .crypto_helper import (
    encrypt,
    decrypt,
    hash_password,
    verify_hash,
    generate_secure_token,
    generate_uuid,
    quick_hash,
    encrypt_sensitive_data,
    decrypt_sensitive_data
)

from .jwt_helper import (
    generate_token,
    verify_token,
    decode_token,
    generate_refresh_token,
    extract_token_from_header,
    get_token_expiration,
    is_token_expired
)

from .logger import (
    logger
)

from .response_handler import (
    success_response,
    error_response,
    validation_error_response,
    paginated_response
)

from .transaction_wrapper import (
    execute_with_transaction,
    execute_query,
)

__all__ = [
    # Crypto
    'encrypt',
    'decrypt',
    'hash_password',
    'verify_hash',
    'generate_secure_token',
    'generate_uuid',
    'quick_hash',
    'encrypt_sensitive_data',
    'decrypt_sensitive_data',
    
    # JWT
    'generate_token',
    'verify_token',
    'decode_token',
    'generate_refresh_token',
    'extract_token_from_header',
    'get_token_expiration',
    'is_token_expired',
    
    # Logger
    'logger',
    
    # Response handlers
    'success_response',
    'error_response',
    'validation_error_response',
    'paginated_response',
    
    # Transaction wrappers
    'execute_with_transaction',
    'execute_query',
]