"""
Service de productos
Equivalente a productService.js
"""

from datetime import datetime
from sqlalchemy import func, case, and_, or_
from src.models.product import Product
from src.models.user import User
from config.database import db
from src.utils import execute_with_transaction, execute_query, logger

class ProductService:
    """Service de productos"""
    
    def create_product(self, product_data, user_id):
        """Crear producto"""
        
        def business_logic(data, session, db_instance):
            # Crear producto
            product = Product(
                name=data['name'],
                description=data.get('description'),
                price=data['price'],
                stock=data.get('stock', 0),
                category=data.get('category'),
                is_active=data.get('is_active', True),
                created_by=data['created_by']
            )
            session.add(product)
            session.flush()
            
            logger.info('Producto creado', extra={
                'productId': product.id,
                'name': product.name,
                'createdBy': user_id
            })
            
            return product.to_dict()
        
        return execute_with_transaction(
            {**product_data, 'created_by': user_id},
            business_logic,
            'createProduct',
            {'db': db}
        )
    
    
    def list_products(self, filters=None):
        """Listar productos con paginación y filtros"""
        if filters is None:
            filters = {}
        
        def query_logic(db_instance):
            page = int(filters.get('page', 1))
            limit = int(filters.get('limit', 10))
            category = filters.get('category')
            is_active = filters.get('isActive')
            min_price = filters.get('minPrice')
            max_price = filters.get('maxPrice')
            search = filters.get('search')
            sort_by = filters.get('sortBy', 'created_at')
            sort_order = filters.get('sortOrder', 'DESC')
            
            offset = (page - 1) * limit
            
            # Construir query base
            query = Product.query
            
            # Aplicar filtros
            if category:
                query = query.filter(Product.category == category)
            
            if is_active is not None:
                # Convertir string a boolean si es necesario
                if isinstance(is_active, str):
                    is_active = is_active.lower() == 'true'
                query = query.filter(Product.is_active == is_active)
            
            if min_price is not None:
                query = query.filter(Product.price >= float(min_price))
            
            if max_price is not None:
                query = query.filter(Product.price <= float(max_price))
            
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Product.name.ilike(search_pattern),
                        Product.description.ilike(search_pattern)
                    )
                )
            
            # Contar total
            total = query.count()
            
            # Aplicar ordenamiento
            order_column = getattr(Product, sort_by, Product.created_at)
            if sort_order.upper() == 'DESC':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
            
            # Aplicar paginación y obtener con relaciones
            products = query.options(
                db_instance.joinedload(Product.creator)
            ).limit(limit).offset(offset).all()
            
            logger.debug('Productos listados', extra={
                'total': total,
                'page': page,
                'limit': limit,
                'filters': filters
            })
            
            return {
                'products': [product.to_dict() for product in products],
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'totalPages': (total + limit - 1) // limit
                }
            }
        
        return execute_query(query_logic, 'listProducts', db)
    
    
    def get_product_by_id(self, product_id):
        """Obtener producto por ID"""
        
        def query_logic(db_instance):
            product = Product.query.options(
                db_instance.joinedload(Product.creator)
            ).get(product_id)
            
            if not product:
                raise Exception('Producto no encontrado')
            
            logger.debug('Producto obtenido por ID', extra={'productId': product_id})
            
            return product.to_dict()
        
        return execute_query(query_logic, 'getProductById', db)
    
    
    def update_product(self, product_id, update_data, user_id):
        """Actualizar producto"""
        
        def business_logic(data, session, db_instance):
            product = Product.query.get(data['productId'])
            
            if not product:
                return {
                    '_rollback': True,
                    'message': 'Producto no encontrado',
                    'data': None
                }
            
            # Campos permitidos para actualizar
            allowed_fields = ['name', 'description', 'price', 'stock', 'category', 'is_active']
            
            for field in allowed_fields:
                if field in data and data[field] is not None:
                    setattr(product, field, data[field])
            
            session.add(product)
            session.flush()
            
            logger.info('Producto actualizado', extra={
                'productId': product.id,
                'updatedBy': user_id
            })
            
            return product.to_dict()
        
        return execute_with_transaction(
            {'productId': product_id, **update_data, 'userId': user_id},
            business_logic,
            'updateProduct',
            {'db': db}
        )
    
    
    def update_stock(self, product_id, quantity, operation):
        """Actualizar stock del producto"""
        
        def business_logic(data, session, db_instance):
            # Lock para evitar condiciones de carrera
            product = Product.query.with_for_update().get(data['productId'])
            
            if not product:
                return {
                    '_rollback': True,
                    'message': 'Producto no encontrado',
                    'data': None
                }
            
            old_stock = product.stock
            
            if data['operation'] == 'add':
                product.stock += data['quantity']
            
            elif data['operation'] == 'subtract':
                if product.stock < data['quantity']:
                    return {
                        '_rollback': True,
                        'message': 'Stock insuficiente',
                        'data': {
                            'currentStock': product.stock,
                            'requested': data['quantity']
                        }
                    }
                product.stock -= data['quantity']
            
            elif data['operation'] == 'set':
                if data['quantity'] < 0:
                    return {
                        '_rollback': True,
                        'message': 'El stock no puede ser negativo',
                        'data': None
                    }
                product.stock = data['quantity']
            
            else:
                return {
                    '_rollback': True,
                    'message': 'Operación inválida',
                    'data': None
                }
            
            session.add(product)
            session.flush()
            
            logger.info('Stock actualizado', extra={
                'productId': product.id,
                'operation': data['operation'],
                'oldStock': old_stock,
                'newStock': product.stock,
                'quantity': data['quantity']
            })
            
            return {
                'productId': product.id,
                'name': product.name,
                'oldStock': old_stock,
                'newStock': product.stock,
                'operation': data['operation']
            }
        
        return execute_with_transaction(
            {'productId': product_id, 'quantity': quantity, 'operation': operation},
            business_logic,
            'updateStock',
            {'db': db, 'isolation_level': 'SERIALIZABLE'}
        )
    
    
    def delete_product(self, product_id):
        """Eliminar producto (soft delete)"""
        
        def business_logic(data, session, db_instance):
            product = Product.query.get(data['productId'])
            
            if not product:
                return {
                    '_rollback': True,
                    'message': 'Producto no encontrado',
                    'data': None
                }
            
            # Soft delete: marcar como inactivo
            product.is_active = False
            session.add(product)
            session.flush()
            
            logger.info('Producto desactivado (soft delete)', extra={
                'productId': product.id
            })
            
            return {
                'message': 'Producto eliminado exitosamente',
                'productId': product.id
            }
        
        return execute_with_transaction(
            {'productId': product_id},
            business_logic,
            'deleteProduct',
            {'db': db}
        )
    
    
    def permanently_delete_product(self, product_id):
        """Eliminar producto permanentemente (hard delete)"""
        
        def business_logic(data, session, db_instance):
            product = Product.query.get(data['productId'])
            
            if not product:
                return {
                    '_rollback': True,
                    'message': 'Producto no encontrado',
                    'data': None
                }
            
            session.delete(product)
            session.flush()
            
            logger.warn('Producto eliminado permanentemente', extra={
                'productId': product.id
            })
            
            return {
                'message': 'Producto eliminado permanentemente',
                'productId': product.id
            }
        
        return execute_with_transaction(
            {'productId': product_id},
            business_logic,
            'permanentlyDeleteProduct',
            {'db': db}
        )
    
    
    def get_products_by_category(self, category):
        """Obtener productos por categoría"""
        
        def query_logic(db_instance):
            products = Product.query.filter(
                and_(
                    Product.category == category,
                    Product.is_active == True
                )
            ).order_by(Product.name.asc()).all()
            
            logger.debug('Productos obtenidos por categoría', extra={
                'category': category,
                'count': len(products)
            })
            
            return [product.to_dict() for product in products]
        
        return execute_query(query_logic, 'getProductsByCategory', db)
    
    
    def get_product_stats(self):
        """Obtener estadísticas de productos"""
        
        def query_logic(db_instance):
            # Realizar consulta SQL directa para estadísticas
            result = db_instance.session.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_active = true) as active,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive,
                    COUNT(*) FILTER (WHERE stock = 0) as "outOfStock",
                    COUNT(*) FILTER (WHERE stock > 0 AND stock <= 10) as "lowStock",
                    AVG(price) as "averagePrice",
                    SUM(stock) as "totalStock"
                FROM products
            """).fetchone()
            
            logger.debug('Estadísticas de productos obtenidas')
            
            # Convertir resultado a diccionario
            stats = {
                'total': int(result[0]) if result[0] else 0,
                'active': int(result[1]) if result[1] else 0,
                'inactive': int(result[2]) if result[2] else 0,
                'outOfStock': int(result[3]) if result[3] else 0,
                'lowStock': int(result[4]) if result[4] else 0,
                'averagePrice': float(result[5]) if result[5] else 0.0,
                'totalStock': int(result[6]) if result[6] else 0
            }
            
            return stats
        
        return execute_query(query_logic, 'getProductStats', db)


# Exportar instancia única
product_service = ProductService()