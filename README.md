# Node.js API Base

API base construida con Node.js, Express, Sequelize y PostgreSQL. Incluye autenticación JWT, seguridad con Helmet, documentación Swagger y estructura modular.

## Requisitos Previos

- Node.js (v14 o superior)
- PostgreSQL
- npm

## Instalación

1.  Clonar el repositorio:

    ```bash
    git clone <url-del-repositorio>
    cd nodejsbase
    ```

2.  Instalar dependencias:
    ```bash
    npm install
    ```

## Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`. Configura las siguientes variables:

```ini
# Server
NODE_ENV=development      # Entorno: development, test, create-vite-appproduction
PORT=3000                 # Puerto del servidor

# API
API_PREFIX=/api/v1       # Prefijo global para las rutas

# CORS
CORS_ORIGIN=*            # Orígenes permitidos (usar dominio específico en producción)

# Database
DB_HOST=localhost        # Host de la base de datos
DB_PORT=5432             # Puerto de PostgreSQL
DB_NAME=tu_base_datos    # Nombre de la base de datos principal
DB_USER=tu_usuario       # Usuario de la base de datos
DB_PASSWORD=tu_password  # Contraseña de la base de datos
DB_DIALECT=postgres      # Dialecto (postgres)
DB_SCHEMA=public         # Esquema de la base de datos

# JWT
JWT_SECRET=tu_secret_super_seguro_cambialo_en_produccion # Clave secreta para firmar tokens
JWT_EXPIRES_IN=24h       # Tiempo de expiración del token

# Crypto
ENCRYPTION_KEY=tu_clave_super_segura_cambiala_en_produccion # Clave para encriptación de datos sensibles

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000 # Ventana de tiempo en ms (15 minutos)
RATE_LIMIT_MAX_REQUESTS=100 # Máximo de peticiones por ventana por IP

# Logs
LOG_LEVEL=debug          # Nivel de log (debug, info, error)
```

### Entorno de Pruebas (.env.test)

Para ejecutar los tests, necesitas configurar un archivo `.env.test`. Este archivo se carga automáticamente cuando `NODE_ENV=test`.

```ini
# Server
NODE_ENV=test
PORT=3000

# API
API_PREFIX=/api/v1

# Base de datos de pruebas (IMPORTANTE: Usar una base de datos distinta a la de desarrollo)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres         # Puede ser la misma instancia
DB_USER=postgres
DB_PASSWORD=tu_password
DB_DIALECT=postgres
DB_SCHEMA=test_schema    # Usar un esquema separado para tests es recomendado

# Claves para tests
JWT_SECRET=clave_secreta_para_tests
JWT_EXPIRES_IN=24h
ENCRYPTION_KEY=clave_encriptacion_para_tests
```

> [!WARNING]
> Asegúrate de que las credenciales de la base de datos de pruebas sean correctas y tengas permisos para crear/borrar esquemas o tablas.

## Base de Datos

Comandos disponibles para gestionar la base de datos con Sequelize:

- **Migrar base de datos:**

  ```bash
  npm run db:migrate
  ```

- **Deshacer última migración:**

  ```bash
  npm run db:migrate:undo
  ```

- **Poblar base de datos (Seeds):**

  ```bash
  npm run db:seed
  ```

- **Resetear base de datos (Undo all + Migrate + Seed):**
  ```bash
  npm run db:reset
  ```

## Ejecución

### Desarrollo

Arranca el servidor con `nodemon` para reinicio automático ante cambios.

```bash
npm run dev
```

### Producción

Arranca el servidor con `node`.

```bash
npm start
```

## Testing

Ejecutar la suite de pruebas con Jest. Asegúrate de tener configurado el archivo `.env.test`.

```bash
npm test
```

Para ejecutar tests en modo watch (re-ejecución automática):

```bash
npm run test:watch
```

## Documentación API

La API se sirve bajo el prefijo configurado (por defecto `/api/v1`).

### Swagger

La documentación interactiva generado con Swagger está disponible en:
`http://localhost:3000/api/v1/docs`

### Endpoints Principales

#### General

- `GET /`: Mensaje de bienvenida y lista de endpoints principales.
- `GET /api/v1/health`: Estado del servicio (Health check).

#### Autenticación (Auth)

- `POST /api/v1/auth/register`: Registrar nuevo usuario.
- `POST /api/v1/auth/login`: Iniciar sesión (retorna JWT).
- `GET /api/v1/auth/profile`: Obtener perfil del usuario autenticado.
- `PUT /api/v1/auth/profile`: Actualizar perfil.
- `PUT /api/v1/auth/change-password`: Cambiar contraseña.
- `DELETE /api/v1/auth/account`: Desactivar cuenta.

#### Usuarios (Users) - Requiere Rol Admin

- `GET /api/v1/users`: Listar usuarios (paginado).
- `GET /api/v1/users/stats`: Estadísticas de usuarios.
- `GET /api/v1/users/:id`: Obtener usuario por ID.
- `PUT /api/v1/users/:id/role`: Cambiar rol de usuario.
- `PUT /api/v1/users/:id/activate`: Activar usuario.
- `PUT /api/v1/users/:id/deactivate`: Desactivar usuario.
- `DELETE /api/v1/users/:id`: Eliminar usuario permanentemente.

#### Productos (Products)

**Público:**

- `GET /api/v1/products`: Listar productos.
- `GET /api/v1/products/:id`: Ver detalle de producto.
- `GET /api/v1/products/category/:category`: Productos por categoría.

**Admin:**

- `GET /api/v1/products/stats`: Estadísticas de productos.
- `POST /api/v1/products`: Crear producto.
- `PUT /api/v1/products/:id`: Actualizar producto.
- `PATCH /api/v1/products/:id/stock`: Actualizar stock.
- `DELETE /api/v1/products/:id`: Eliminar producto (soft delete).
- `DELETE /api/v1/products/:id/permanent`: Eliminar producto permanentemente.

## Estructura del Proyecto

```
nodejsBase/
├─ config/         # Configuraciones (DB, Swagger)
├─ migrations/         # Migraciones de la base de datos
├─ seeds/         # Semillas de la base de datos
├─ tests/         # Pruebas unitarias y de integración
├─ src/
   ├── controllers/    # Lógica de los endpoints (Handlers)
   ├── middlewares/    # Middlewares (Auth, Error Handler, Validator)
   ├── models/         # Modelos Sequelize
   ├── routes/         # Definición de rutas
   ├── services/       # Lógica de negocio
   ├── utils/          # Utilidades y Helpers
   └── validators/     # Validaciones con express-validator
```
