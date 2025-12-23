"""
Seed de productos demo
Equivalente a 20251218203949-demo-products.js
"""
from config.database import db
from src.models import User, Product
from decimal import Decimal


def seed_products():
    """Crea productos de demostración"""
    
    # Verificar si ya existen productos
    existing_products = Product.query.count()
    if existing_products > 0:
        print(f"⚠️  Ya existen {existing_products} productos. Saltando seed de productos...")
        return
    
    # Obtener usuario admin como creador
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if not admin:
        print("❌ No se encontró usuario admin. Ejecuta primero el seed de usuarios.")
        return
    
    products_data = [
        {
            'name': 'Laptop HP',
            'description': 'Laptop HP Pavilion 15.6" Intel Core i5 8GB RAM 256GB SSD',
            'price': Decimal('599.99'),
            'stock': 10,
            'category': 'Electrónica',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Mouse Logitech',
            'description': 'Mouse inalámbrico Logitech M185 con sensor óptico',
            'price': Decimal('15.99'),
            'stock': 50,
            'category': 'Accesorios',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Teclado Mecánico',
            'description': 'Teclado mecánico RGB retroiluminado switches azules',
            'price': Decimal('89.99'),
            'stock': 25,
            'category': 'Accesorios',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Monitor Samsung',
            'description': 'Monitor Samsung 24" Full HD 75Hz FreeSync',
            'price': Decimal('179.99'),
            'stock': 15,
            'category': 'Electrónica',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Webcam HD',
            'description': 'Webcam 1080p con micrófono integrado',
            'price': Decimal('49.99'),
            'stock': 30,
            'category': 'Accesorios',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Auriculares Bluetooth',
            'description': 'Auriculares inalámbricos con cancelación de ruido',
            'price': Decimal('129.99'),
            'stock': 20,
            'category': 'Audio',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'SSD 1TB',
            'description': 'Disco SSD NVMe M.2 1TB lectura 3500MB/s',
            'price': Decimal('99.99'),
            'stock': 40,
            'category': 'Almacenamiento',
            'is_active': True,
            'created_by': admin.id
        },
        {
            'name': 'Producto Inactivo',
            'description': 'Este producto está desactivado',
            'price': Decimal('0.01'),
            'stock': 0,
            'category': 'Test',
            'is_active': False,
            'created_by': admin.id
        }
    ]
    
    try:
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"✅ {len(products_data)} productos creados correctamente")
        
        # Mostrar resumen por categoría
        categories = {}
        for product_data in products_data:
            cat = product_data['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("   Productos por categoría:")
        for cat, count in categories.items():
            print(f"   - {cat}: {count}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear productos: {str(e)}")
        raise