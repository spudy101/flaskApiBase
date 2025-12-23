"""
Gestor de seeds - equivalente al CLI de Sequelize
"""
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from config.settings import config
from config.database import db, init_db


def create_seed_app():
    """Crea app de Flask para ejecutar seeds"""
    env = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config[env])
    init_db(app)
    return app


def run_seeds(seed_name=None):
    """
    Ejecuta seeds
    
    Args:
        seed_name: Nombre específico del seed o 'all' para todos
    """
    app = create_seed_app()
    
    with app.app_context():
        if seed_name == 'all' or seed_name is None:
            print("🌱 Ejecutando todos los seeds...")
            from seeds.demo_users import seed_users
            from seeds.demo_products import seed_products
            
            seed_users()
            seed_products()
            print("✅ Seeds completados!")
            
        elif seed_name == 'users':
            print("🌱 Ejecutando seed de usuarios...")
            from seeds.demo_users import seed_users
            seed_users()
            print("✅ Seed de usuarios completado!")
            
        elif seed_name == 'products':
            print("🌱 Ejecutando seed de productos...")
            from seeds.demo_products import seed_products
            seed_products()
            print("✅ Seed de productos completado!")
            
        else:
            print(f"❌ Seed '{seed_name}' no encontrado")
            print("Seeds disponibles: users, products, all")


def undo_seeds(seed_name=None):
    """
    Deshace seeds (limpia datos)
    
    Args:
        seed_name: Nombre específico del seed o 'all' para todos
    """
    app = create_seed_app()
    
    with app.app_context():
        from src.models import User, Product, LoginAttempt
        
        if seed_name == 'all' or seed_name is None:
            print("🗑️  Limpiando todos los datos...")
            Product.query.delete()
            User.query.delete()
            LoginAttempt.query.delete()
            db.session.commit()
            print("✅ Datos limpiados!")
            
        elif seed_name == 'users':
            print("🗑️  Limpiando usuarios...")
            User.query.delete()
            db.session.commit()
            print("✅ Usuarios eliminados!")
            
        elif seed_name == 'products':
            print("🗑️  Limpiando productos...")
            Product.query.delete()
            db.session.commit()
            print("✅ Productos eliminados!")
            
        else:
            print(f"❌ Seed '{seed_name}' no encontrado")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestor de seeds')
    parser.add_argument('action', choices=['seed', 'undo'], help='Acción a ejecutar')
    parser.add_argument('--name', default='all', help='Nombre del seed (default: all)')
    
    args = parser.parse_args()
    
    if args.action == 'seed':
        run_seeds(args.name)
    elif args.action == 'undo':
        undo_seeds(args.name)