"""
Middlewares module - Middlewares para Flask
"""

# Error handling
from .error_handler import (
    error_handler,
    not_found_handler
)

# Rate limiting
from .rate_limiter import (
    limiter,
    CREATE_LIMIT,
    rate_limit_exceeded_handler,
    get_general_limit
)

# Request lock
from .request_lock import (
    generate_request_key,
    request_lock,
    get_request_lock_stats,
    clear_request_store
)

# Authentication & Authorization
from .auth_middleware import (
    authenticate,
    authorize,
    authorize_owner_or_admin,
    optional_auth
)

# Validation (wrapper)
from .validate_request import (
    validate_request
)

__all__ = [
    # Error handling
    'error_handler',
    'not_found_handler',
    
    # Rate limiting
    'limiter', 
    'rate_limit_exceeded_handler', 
    'get_general_limit',
    'CREATE_LIMIT',
    
    # Request lock
    'generate_request_key',
    'request_lock',
    'get_request_lock_stats',
    'clear_request_store',
    
    # Authentication & Authorization
    'authenticate',
    'authorize',
    'authorize_owner_or_admin',
    'optional_auth',
    'get_current_user',
    'require_user',
    'is_admin',
    
    # Validation
    'validate_request'
]