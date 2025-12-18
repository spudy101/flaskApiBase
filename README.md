# Flask API Base

Proyecto base en Flask equivalente a Node.js/Express, diseñado para crear APIs RESTful empresariales con las mejores prácticas.

## 🚀 Características

- **Flask** como framework web (equivalente a Express)
- **SQLAlchemy** como ORM (equivalente a Sequelize)
- **Flask-JWT-Extended** para autenticación JWT
- **Blueprints** para organización de rutas (equivalente a Express Router)
- **Auto-generación de modelos** desde la base de datos
- **Transacciones** con rollback automático
- **Middlewares** de autenticación, rate limiting y request locking
- **Cifrado AES-256** para datos sensibles
- **Swagger/OpenAPI** para documentación
- **Logging estructurado** y manejo de errores
- **Docker** para despliegue
- **Pool de conexiones** optimizado

## 📋 Requisitos

- Python 3.9+
- MySQL 5.7+ o PostgreSQL 12+
- pip (gestor de paquetes de Python)

## ⚡ Quick Start

### 1. Instalación

```bash
# Clonar el repositorio
git clone <tu-repo>
cd flask-api-base

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Variables de entorno importantes:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=tu_database
DB_PORT=3306
DB_DIALECT=mysql  # o postgresql

SECRET_KEY=tu-clave-secreta
JWT_SECRET_KEY=tu-jwt-secret
AES_KEY=tu-aes-key-32-bytes-hex
AES_IV=tu-aes-iv-16-bytes-hex
```

### 3. Generar Modelos

```bash
# Generar modelos automáticamente desde tu base de datos
python generar_modelos.py
```

Esto creará el archivo `src/models/generated_models.py` con todos tus modelos.

### 4. Ejecutar

```bash
# Modo desarrollo
python index.py

# O con flask run
export FLASK_APP=index.py
flask run
```

El servidor estará corriendo en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
flask-api-base/
├── index.py                    # Punto de entrada (equivalente a index.js)
├── requirements.txt            # Dependencias (equivalente a package.json)
├── .env.example               # Plantilla de variables de entorno
├── Dockerfile                 # Configuración Docker
├── generar_modelos.py         # Script para generar modelos (equivalente a generar-modelos.js)
│
└── src/
    ├── app.py                 # Configuración de Flask (equivalente a app.js)
    │
    ├── config/                # Configuraciones
    │   ├── database.py        # Config de BD (equivalente a database.js)
    │   ├── swagger.py         # Config de Swagger
    │   └── logging_config.py  # Config de logging
    │
    ├── database/              # Capa de base de datos
    │   └── connection.py      # Conexión SQLAlchemy (equivalente a connection.js)
    │
    ├── models/                # Modelos de base de datos
    │   └── generated_models.py # Modelos autogenerados
    │
    ├── routes/                # Rutas (Blueprints)
    │   ├── __init__.py        # Registro de rutas (equivalente a routes/index.js)
    │   └── perfil_routes.py   # Ejemplo de rutas
    │
    ├── controllers/           # Controladores
    │   └── perfil_controller.py
    │
    ├── services/              # Lógica de negocio
    │   └── perfil_service.py
    │
    ├── middlewares/           # Middlewares
    │   ├── auth_middleware.py      # Autenticación (equivalente a authMiddleware.js)
    │   ├── request_lock_middleware.py # Request locking
    │   └── rate_limit.py           # Rate limiting
    │
    └── utils/                 # Utilidades
        ├── crypto_utils.py    # Cifrado (equivalente a cryptoUtils.js)
        ├── database_utils.py  # Transacciones (equivalente a databaseUtils.js)
        ├── datos_utils.py     # Datos de usuario
        └── request_lock.py    # Sistema de locks
```

## 🔑 Características Principales

### 1. Transacciones Automáticas

```python
from src.utils.database_utils import execute_with_transaction

def crear_usuario(data):
    return execute_with_transaction(
        data,
        lambda params: Usuario.crear(params),
        'CREAR_USUARIO'
    )
```

### 2. Consultas con Logging

```python
from src.utils.database_utils import execute_query

def obtener_usuario(user_id):
    return execute_query(
        {'user_id': user_id},
        lambda params: Usuario.query.get(params['user_id']),
        'OBTENER_USUARIO'
    )
```

### 3. Middlewares de Autenticación

```python
from src.middlewares import verificar_autenticacion, verificar_timestamp

@app.route('/perfil')
@verificar_timestamp
@verificar_autenticacion
def get_perfil():
    return jsonify(usuario=request.usuario)
```

### 4. Request Locking

```python
from src.middlewares import with_request_lock

@app.route('/operacion')
@verificar_autenticacion
@with_request_lock(lambda: request.usuario.get('id_usuario'))
def operacion_critica():
    # Solo una request por usuario a la vez
    return jsonify(status='ok')
```

### 5. Cifrado AES-256

```python
from src.utils.crypto_utils import encriptar_mensaje, desencriptar_mensaje

# Encriptar
encrypted = encriptar_mensaje("datos sensibles")

# Desencriptar
decrypted = desencriptar_mensaje(encrypted)
```

## 🔒 Seguridad

- **JWT** con cookies HttpOnly
- **Cifrado AES-256-CBC** para datos sensibles
- **Rate limiting** configurable
- **CORS** configurable por entorno
- **Helmet-like headers** con Flask-Talisman (opcional)
- **Validación de timestamp** para prevenir replay attacks
- **Request locking** para prevenir operaciones duplicadas

## 📚 Documentación API

Con el servidor corriendo en modo desarrollo:
- Swagger UI: http://localhost:5000/api-docs/

## 🐳 Docker

```bash
# Construir imagen
docker build -t flask-api-base .

# Ejecutar contenedor
docker run -p 5000:5000 --env-file .env flask-api-base
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-flask

# Ejecutar tests
pytest
```

## 📝 Comparación Node.js vs Flask

| Node.js/Express | Flask |
|----------------|-------|
| `express.Router()` | `Blueprint()` |
| `app.use(middleware)` | `@decorator` |
| `async/await` | `async def` (opcional) |
| `try/catch` | `try/except` |
| `require()` | `import` |
| `module.exports` | `__all__` |
| Sequelize | SQLAlchemy |
| `npm install` | `pip install` |
| `package.json` | `requirements.txt` |
| `node index.js` | `python index.py` |

## 🚀 Despliegue

### Con Gunicorn (Producción)

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar
gunicorn -w 4 -b 0.0.0.0:5000 "src.app:create_app()"
```

### Variables de Entorno Importantes

```env
FLASK_ENV=production
PORT=5000
DB_HOST=tu-servidor-bd
SECRET_KEY=clave-super-secreta
```

## 📖 Migración desde Node.js

Si vienes de Node.js/Express, aquí están las equivalencias principales:

1. **Express Router → Flask Blueprint**
2. **Middleware functions → Decorators**
3. **Sequelize → SQLAlchemy**
4. **package.json → requirements.txt**
5. **Callbacks → Return values**

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 💡 Notas Importantes

- **Revisa los modelos generados** y ajusta según sea necesario
- **Configura las variables de entorno** correctamente
- **No uses sync/alter en producción** (igual que en Sequelize)
- **Implementa migraciones** con Alembic para cambios de esquema
- **Revisa la lógica de datos_utils.py** y actualízala con tus modelos reales

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas, abre un issue en el repositorio.
