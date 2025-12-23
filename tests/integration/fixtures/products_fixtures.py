"""
Fixtures adicionales para tests de productos
"""

import pytest
from datetime import datetime
from src.models.product import Product


@pytest.fixture
def create_product(session, test_user):
    """
    Factory fixture para crear productos en la base de datos
    """
    created_products = []
    
    def _create_product(
        name='Test Product',
        description='Test product description',
        price=99.99,
        stock=100,
        category='electronics',
        is_active=True,
        created_by=None
    ):
        """Crea un producto en la base de datos"""
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            is_active=is_active,
            created_by=created_by or test_user.id
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        created_products.append(product)
        return product
    
    yield _create_product
    
    # Cleanup
    for product in created_products:
        session.delete(product)
    session.commit()


@pytest.fixture
def test_product(create_product):
    """
    Producto de prueba pre-creado
    """
    return create_product(
        name='Test Product',
        description='A test product',
        price=50.00,
        stock=100,
        category='electronics'
    )


@pytest.fixture
def inactive_product(create_product):
    """
    Producto inactivo de prueba
    """
    return create_product(
        name='Inactive Product',
        price=25.00,
        stock=50,
        is_active=False
    )


@pytest.fixture
def out_of_stock_product(create_product):
    """
    Producto sin stock
    """
    return create_product(
        name='Out of Stock Product',
        price=75.00,
        stock=0
    )


@pytest.fixture
def sample_create_product_payload():
    """
    Payload válido para crear producto
    """
    return {
        'name': 'New Product',
        'description': 'A new product description',
        'price': 149.99,
        'stock': 50,
        'category': 'electronics',
        'is_active': True
    }


@pytest.fixture
def sample_update_product_payload():
    """
    Payload válido para actualizar producto
    """
    return {
        'name': 'Updated Product Name',
        'price': 199.99,
        'stock': 75
    }


@pytest.fixture
def sample_update_stock_payload():
    """
    Payload válido para actualizar stock
    """
    return {
        'quantity': 10,
        'operation': 'add'
    }