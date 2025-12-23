"""
Centralizar todos los paths
"""

from .auth import auth_paths
# from .products import product_paths
# from .orders import order_paths
# from .payments import payment_paths

def get_all_paths():
    """
    Combina todos los paths en un solo diccionario
    """
    all_paths = {}
    all_paths.update(auth_paths)
    # all_paths.update(product_paths)
    # all_paths.update(order_paths)
    # all_paths.update(payment_paths)
    
    return all_paths