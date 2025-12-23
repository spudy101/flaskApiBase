"""
Centralizar todos los schemas
"""

from .common import common_schemas
from .auth import auth_schemas
from .products import product_schemas
# from .orders import order_schemas
# from .payments import payment_schemas

def get_all_schemas():
    """
    Combina todos los schemas en un solo diccionario
    """
    all_schemas = {}
    all_schemas.update(common_schemas)
    all_schemas.update(auth_schemas)
    all_schemas.update(product_schemas)
    # all_schemas.update(order_schemas)
    # all_schemas.update(payment_schemas)
    
    return all_schemas