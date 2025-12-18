# Ejemplos de Uso

Este archivo contiene ejemplos prácticos de cómo usar las diferentes funcionalidades del proyecto Flask.

## 1. Crear una Nueva Ruta

### Paso 1: Crear el Service

```python
# src/services/producto_service.py
from src.utils.database_utils import execute_query, execute_with_transaction

def obtener_productos():
    """Obtiene todos los productos"""
    def query_logic(params):
        # from src.models import Producto
        # return Producto.query.all()
        return []  # Ejemplo
    
    return execute_query({}, query_logic, 'OBTENER_PRODUCTOS')

def crear_producto(data):
    """Crea un nuevo producto"""
    def business_logic(params):
        # from src.models import Producto
        # producto = Producto(**params)
        # db.session.add(producto)
        return {'id': 1}  # Ejemplo
    
    return execute_with_transaction(data, business_logic, 'CREAR_PRODUCTO')
```

### Paso 2: Crear el Controller

```python
# src/controllers/producto_controller.py
from flask import request, jsonify
from src.services.producto_service import obtener_productos, crear_producto

def get_productos_handler():
    """Handler para obtener productos"""
    try:
        result = obtener_productos()
        
        if result.get('success'):
            return jsonify({
                'data': result['data'],
                'message': 'Productos obtenidos exitosamente',
                'estado_solicitud': 1
            }), 200
        else:
            return jsonify({
                'message': 'Error al obtener productos',
                'estado_solicitud': 0
            }), 500
    except Exception as error:
        return jsonify({
            'message': str(error),
            'estado_solicitud': 0
        }), 500

def crear_producto_handler():
    """Handler para crear producto"""
    try:
        data = request.get_json()
        result = crear_producto(data)
        
        if result.get('success'):
            return jsonify({
                'data': result['data'],
                'message': 'Producto creado exitosamente',
                'estado_solicitud': 1
            }), 201
        else:
            return jsonify({
                'message': result.get('message'),
                'estado_solicitud': 0
            }), 500
    except Exception as error:
        return jsonify({
            'message': str(error),
            'estado_solicitud': 0
        }), 500
```

### Paso 3: Crear las Rutas

```python
# src/routes/producto_routes.py
from flask import Blueprint
from src.controllers.producto_controller import get_productos_handler, crear_producto_handler
from src.middlewares.auth_middleware import verificar_autenticacion

producto_bp = Blueprint('productos', __name__, url_prefix='/productos')

@producto_bp.route('/', methods=['GET'])
@verificar_autenticacion
def get_productos():
    """
    Obtener todos los productos
    ---
    tags:
      - productos
    responses:
      200:
        description: Lista de productos
    """
    return get_productos_handler()

@producto_bp.route('/', methods=['POST'])
@verificar_autenticacion
def crear_producto():
    """
    Crear un nuevo producto
    ---
    tags:
      - productos
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            nombre:
              type: string
            precio:
              type: number
    """
    return crear_producto_handler()
```

### Paso 4: Registrar el Blueprint

```python
# src/routes/__init__.py
from flask import Flask
from .perfil_routes import perfil_bp
from .producto_routes import producto_bp  # Agregar

def register_routes(app: Flask):
    app.register_blueprint(perfil_bp)
    app.register_blueprint(producto_bp)  # Agregar
    
    print("✅ Rutas registradas:")
    print("   - /perfil_usuario/*")
    print("   - /productos/*")  # Agregar
```

## 2. Usar Request Locking

```python
from src.middlewares.request_lock_middleware import with_request_lock

@producto_bp.route('/operacion-critica', methods=['POST'])
@verificar_autenticacion
@with_request_lock(lambda: request.usuario.get('id_usuario'))
def operacion_critica():
    """
    Solo permite una request por usuario a la vez
    """
    # Tu lógica aquí
    return jsonify({'status': 'ok'}), 200
```

## 3. Usar Cifrado

```python
from src.utils.crypto_utils import encriptar_mensaje, desencriptar_mensaje

# Encriptar datos sensibles
datos_sensibles = "información confidencial"
encrypted = encriptar_mensaje(datos_sensibles)

# Desencriptar
decrypted = desencriptar_mensaje(encrypted)
```

## 4. Trabajar con Transacciones

```python
from src.utils.database_utils import execute_with_transaction
from src.database.connection import db

def transferir_dinero(data):
    """Ejemplo de transacción compleja"""
    def business_logic(params):
        # Todas estas operaciones se ejecutan en una transacción
        # Si algo falla, se hace rollback automático
        
        # from src.models import Cuenta
        
        # cuenta_origen = Cuenta.query.get(params['cuenta_origen_id'])
        # cuenta_destino = Cuenta.query.get(params['cuenta_destino_id'])
        
        # cuenta_origen.saldo -= params['monto']
        # cuenta_destino.saldo += params['monto']
        
        # db.session.add(cuenta_origen)
        # db.session.add(cuenta_destino)
        
        return {'transferencia_id': 123}
    
    return execute_with_transaction(data, business_logic, 'TRANSFERIR_DINERO')
```

## 5. Consultas con Relaciones

```python
def obtener_usuario_completo(user_id):
    """Ejemplo de consulta con joins"""
    def query_logic(params):
        # from src.models import Usuario, Persona, Rol
        
        # usuario = Usuario.query.filter_by(
        #     id_usuario=params['user_id']
        # ).join(Persona).join(Rol).first()
        
        # if not usuario:
        #     return None
        
        # return {
        #     'id': usuario.id_usuario,
        #     'nombre': usuario.persona.nombres,
        #     'rol': usuario.rol.nombre_rol
        # }
        
        return None
    
    return execute_query(
        {'user_id': user_id},
        query_logic,
        'OBTENER_USUARIO_COMPLETO'
    )
```

## 6. Validación de Datos

```python
from marshmallow import Schema, fields, ValidationError

class ProductoSchema(Schema):
    nombre = fields.Str(required=True, validate=lambda x: len(x) > 0)
    precio = fields.Float(required=True, validate=lambda x: x > 0)
    descripcion = fields.Str()

@producto_bp.route('/', methods=['POST'])
@verificar_autenticacion
def crear_producto():
    try:
        # Validar datos
        schema = ProductoSchema()
        data = schema.load(request.get_json())
        
        # Crear producto
        result = crear_producto(data)
        return jsonify(result), 201
        
    except ValidationError as err:
        return jsonify({
            'message': 'Datos inválidos',
            'errors': err.messages
        }), 400
```

## 7. Manejo de Archivos

```python
from flask import request
import os

@producto_bp.route('/upload', methods=['POST'])
@verificar_autenticacion
def upload_imagen():
    if 'file' not in request.files:
        return jsonify({'message': 'No se proporcionó archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'Archivo vacío'}), 400
    
    # Guardar archivo
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'Archivo subido exitosamente',
        'filename': filename
    }), 200
```

## 8. Rate Limiting Personalizado

```python
from flask_limiter import Limiter

# En src/app.py
limiter = Limiter(
    app=app,
    key_func=get_remote_address
)

# En tus rutas
@producto_bp.route('/operacion-costosa', methods=['POST'])
@limiter.limit("5 per minute")  # Máximo 5 requests por minuto
@verificar_autenticacion
def operacion_costosa():
    # Tu lógica aquí
    return jsonify({'status': 'ok'}), 200
```

## 9. Testing

```python
# tests/test_productos.py
import pytest
from src.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_productos(client):
    """Test obtener productos"""
    response = client.get('/productos/')
    assert response.status_code == 200
    
def test_crear_producto(client):
    """Test crear producto"""
    data = {
        'nombre': 'Producto Test',
        'precio': 100.0
    }
    response = client.post('/productos/', json=data)
    assert response.status_code == 201
```

## 10. Variables de Entorno

```python
import os

# En cualquier archivo
db_host = os.getenv('DB_HOST', 'localhost')
secret_key = os.getenv('SECRET_KEY')
debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Validar que existan
required_vars = ['DB_HOST', 'DB_USER', 'SECRET_KEY']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Variables faltantes: {missing}")
```

## 11. Logging

```python
from flask import current_app

def mi_funcion():
    current_app.logger.info('Información general')
    current_app.logger.warning('Advertencia')
    current_app.logger.error('Error', exc_info=True)
    current_app.logger.debug('Debug detallado')
```

## 12. Background Tasks (opcional con Celery)

```python
# Si necesitas tareas en background, considera usar Celery
# pip install celery redis

from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def enviar_email_async(email, mensaje):
    # Tu lógica de envío de email
    pass

# Usar en tu código
enviar_email_async.delay('user@example.com', 'Hola!')
```

## Tips Adicionales

1. **Siempre usa transacciones** para operaciones de escritura
2. **Valida los datos** antes de procesarlos
3. **Maneja errores específicos** en lugar de capturar todo
4. **Usa logging** en lugar de print()
5. **Documenta tus endpoints** con Swagger
6. **Escribe tests** para funcionalidad crítica
7. **Usa type hints** en Python 3.9+
8. **Revisa el código** con flake8 o pylint
9. **Formatea con black** para consistencia
10. **Usa virtual environments** siempre

¡Listo para empezar! 🚀
