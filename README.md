# Flask API Base

API base construida con **Flask** y **PostgreSQL**, con una estructura modular y preparada para crecer.  
Incluye autenticación JWT, configuración de seguridad, documentación con Swagger/OpenAPI y buenas prácticas para el manejo de entornos.

---

## Requisitos Previos

- Python **3.9 o superior**
- PostgreSQL
- pip (incluido con Python)

---

## Instalación

### 1️⃣ Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd flask-api-base
```

---

### 2️⃣ Crear un entorno virtual

Se recomienda usar un entorno virtual para aislar las dependencias del proyecto.

```bash
python -m venv env
```

Esto creará una carpeta llamada `env` que contendrá el entorno virtual del proyecto.

---

### 3️⃣ Activar el entorno virtual

#### Windows (PowerShell / CMD)
```bash
env\Scripts\activate
```

#### Linux / macOS
```bash
source env/bin/activate
```

Cuando el entorno esté activo, verás `(env)` al inicio de la terminal.

---

### 4️⃣ Instalar dependencias

Con el entorno virtual activado, instala los paquetes necesarios:

```bash
pip install -r requirements.txt
```

Esto instalará Flask y todas las dependencias del proyecto dentro del entorno virtual.

---

## Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`. Configura las siguientes variables:

```ini
# Server
FLASK_ENV=development      # Entorno: development, test, production
FLASK_DEBUG=True
PORT=5000                 # Puerto del servidor

# API
API_PREFIX=/api/v1        # Prefijo global para las rutas

# CORS
CORS_ORIGIN=*             # Orígenes permitidos (usar dominio específico en producción)

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tu_base_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_password

# JWT
JWT_SECRET=tu_secret_super_seguro_cambialo_en_produccion
JWT_EXPIRES_IN=24h

# Crypto
ENCRYPTION_KEY=tu_clave_super_segura_cambiala_en_produccion

# Logs
LOG_LEVEL=debug
```

---

## Base de Datos

La aplicación utiliza **SQLAlchemy** y **Flask-Migrate** para la gestión de la base de datos.

- **Inicializar migraciones**
```bash
flask db init
```

- **Crear migración**
```bash
flask db migrate -m "mensaje de migración"
```

- **Aplicar migraciones**
```bash
flask db upgrade
```

- **Revertir última migración**
```bash
flask db downgrade
```

---

## Ejecución

### Desarrollo

Arranca la aplicación ejecutando el archivo principal:

```bash
python run.py
```

> Asegúrate de tener el entorno virtual activado antes de ejecutar el proyecto.

---

### Producción

Ejemplo usando **Gunicorn**:

```bash
gunicorn run:app
```

---

## Testing

Las pruebas están implementadas en Python.

Para ejecutar los tests:

```bash
pytest
```

📌 **Nota importante:**  
Para entender en detalle cómo están organizadas las pruebas, los fixtures y los escenarios de testing, revisa el archivo **README.md dentro de la carpeta `tests/`**.

---

## Documentación API

La API se sirve bajo el prefijo configurado (por defecto `/api/v1`).

### Swagger

La documentación interactiva generada con Swagger/OpenAPI está disponible en:
```
http://localhost:5000/api/v1/docs
```

---

## Endpoints Principales

### General

- `GET /` : Mensaje de bienvenida y lista de endpoints principales.
- `GET /api/v1/health` : Estado del servicio (Health check).

---

### Autenticación (Auth)

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/profile`
- `PUT /api/v1/auth/profile`
- `PUT /api/v1/auth/change-password`
- `DELETE /api/v1/auth/account`

---

### Usuarios (Users) - Requiere Rol Admin

- `GET /api/v1/users`
- `GET /api/v1/users/stats`
- `GET /api/v1/users/<id>`
- `PUT /api/v1/users/<id>/role`
- `PUT /api/v1/users/<id>/activate`
- `PUT /api/v1/users/<id>/deactivate`
- `DELETE /api/v1/users/<id>`

---

### Productos (Products)

**Público:**

- `GET /api/v1/products`
- `GET /api/v1/products/<id>`
- `GET /api/v1/products/category/<category>`

**Admin:**

- `GET /api/v1/products/stats`
- `POST /api/v1/products`
- `PUT /api/v1/products/<id>`
- `PATCH /api/v1/products/<id>/stock`
- `DELETE /api/v1/products/<id>`
- `DELETE /api/v1/products/<id>/permanent`

---

## Estructura del Proyecto

```text
flask-api-base/
├─ config/          # Configuraciones (DB, Swagger)
├─ migrations/      # Migraciones de la base de datos
├─ tests/           # Pruebas unitarias y de integración (ver README.md interno)
├─ src/
│  ├─ controllers/  # Lógica de los endpoints
│  ├─ middlewares/  # Middlewares (Auth, Error Handler)
│  ├─ models/       # Modelos SQLAlchemy
│  ├─ routes/       # Definición de rutas
│  ├─ services/     # Lógica de negocio
│  └─ utils/        # Utilidades y helpers
├─ run.py           # Punto de entrada de la aplicación
└─ requirements.txt
```
