"""
Models package
Exporta todos los modelos y los inicializa con db
"""
from config.database import db
from .user import User as UserClass
from .product import Product as ProductClass
from .login_attempt import LoginAttempt as LoginAttemptClass

# Definir modelos con db
User = UserClass.define_model(db)
Product = ProductClass.define_model(db)
LoginAttempt = LoginAttemptClass.define_model(db)

__all__ = ['User', 'Product', 'LoginAttempt']
