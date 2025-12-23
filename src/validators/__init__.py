"""
Validators module - Schemas de validación usando Marshmallow
"""

# Auth validators
from .auth_validator import (
    RegisterSchema,
    LoginSchema,
    UpdateProfileSchema,
    ChangePasswordSchema,
    validate_register,
    validate_login,
    validate_update_profile,
    validate_change_password
)

# Product validators
from .product_validator import (
    CreateProductSchema,
    UpdateProductSchema,
    ProductIdParamSchema,
    ListProductsSchema,
    UpdateStockSchema,
    validate_create_product,
    validate_update_product,
    validate_product_id,
    validate_list_products,
    validate_update_stock
)

# Common validators
from .common_validator import (
    UUIDParamSchema,
    CustomUUIDParamSchema,
    PaginationSchema,
    SortSchema,
    SearchSchema,
    DateRangeSchema,
    PaginationWithSearchSchema,
    FullQuerySchema,
    validate_uuid_param,
    validate_pagination,
    validate_sort,
    validate_search,
    validate_date_range
)

__all__ = [
    # Auth validators
    'RegisterSchema',
    'LoginSchema',
    'UpdateProfileSchema',
    'ChangePasswordSchema',
    'validate_register',
    'validate_login',
    'validate_update_profile',
    'validate_change_password',
    
    # Product validators
    'CreateProductSchema',
    'UpdateProductSchema',
    'ProductIdParamSchema',
    'ListProductsSchema',
    'UpdateStockSchema',
    'validate_create_product',
    'validate_update_product',
    'validate_product_id',
    'validate_list_products',
    'validate_update_stock',
    
    # Common validators
    'UUIDParamSchema',
    'CustomUUIDParamSchema',
    'PaginationSchema',
    'SortSchema',
    'SearchSchema',
    'DateRangeSchema',
    'PaginationWithSearchSchema',
    'FullQuerySchema',
    'validate_uuid_param',
    'validate_pagination',
    'validate_sort',
    'validate_search',
    'validate_date_range'
]