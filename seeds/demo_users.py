"""
Seed de usuarios demo
Equivalente a 20251218203259-demo-users.js
"""
from config.database import db
from src.models import User
from datetime import datetime


def seed_users():
    """Crea usuarios de demostración"""
    
    # Verificar si ya existen usuarios
    existing_users = User.query.count()
    if existing_users > 0:
        print(f"⚠️  Ya existen {existing_users} usuarios. Saltando seed de usuarios...")
        return
    
    users_data = [
        {
            'email': 'admin@example.com',
            'password': 'Admin123!',  # Se hasheará automáticamente por el hook
            'name': 'Administrador',
            'role': 'admin',
            'is_active': True,
            'last_login': None
        },
        {
            'email': 'user1@example.com',
            'password': 'User123!',
            'name': 'Usuario Demo 1',
            'role': 'user',
            'is_active': True,
            'last_login': None
        },
        {
            'email': 'user2@example.com',
            'password': 'User123!',
            'name': 'Usuario Demo 2',
            'role': 'user',
            'is_active': True,
            'last_login': None
        },
        {
            'email': 'inactive@example.com',
            'password': 'Inactive123!',
            'name': 'Usuario Inactivo',
            'role': 'user',
            'is_active': False,
            'last_login': None
        }
    ]
    
    try:
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ {len(users_data)} usuarios creados correctamente")
        
        # Mostrar info de usuarios creados
        for user_data in users_data:
            print(f"   - {user_data['email']} ({user_data['role']})")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear usuarios: {str(e)}")
        raise