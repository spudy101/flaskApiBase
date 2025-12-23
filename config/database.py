from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa la base de datos"""
    db.init_app(app)
    
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from src.models import User, Product, LoginAttempt  # noqa
        
        print(f"✅ Modelos registrados: User, Product, LoginAttempt")
        print(f"✅ Schema: {app.config.get('DB_SCHEMA', 'public')}")