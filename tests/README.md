# Testing Guide - Flask Auth Module

Esta guía documenta la estrategia de testing para el módulo de autenticación, con ejemplos que puedes replicar en otros módulos.

## 📁 Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py                          # Fixtures globales (app, db, client)
├── pytest.ini                           # Configuración de pytest
│
├── unit/                                # Tests unitarios (con mocks)
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures de mocking
│   └── services/
│       ├── __init__.py
│       ├── test_auth_service.py         # Tests de autenticación
│       ├── test_product_service.py      # Tests de productos
│       └── test_user_service.py         # Tests de usuarios
│
└── integration/                         # Tests de integración (con DB)
    ├── __init__.py
    ├── conftest.py                      # Fixtures de DB y datos
    ├── fixtures/
    │   ├── __init__.py
    │   └── products_fixtures.py         # Fixtures específicas de productos
    ├── services/
    │   ├── __init__.py
    │   ├── test_auth_service_db.py      # Tests de autenticación
    │   ├── test_product_service_db.py   # Tests de productos
    │   └── test_user_service_db.py      # Tests de usuarios
    └── routes/
        ├── __init__.py
        ├── test_auth_routes.py          # Endpoints de autenticación
        ├── test_product_routes.py       # Endpoints de productos
        └── test_user_routes.py          # Endpoints de usuarios

```

## 🎯 Filosofía de Testing

### Tests Unitarios (unit/)
- **Objetivo**: Testear lógica de negocio aislada
- **Estrategia**: Mockear completamente la base de datos
- **Velocidad**: Muy rápidos (sin I/O)
- **Casos de uso**: 
  - Validaciones
  - Cálculos
  - Transformaciones de datos
  - Lógica de bloqueos/intentos

### Tests de Integración - Services (integration/services/)
- **Objetivo**: Verificar que queries SQL y transacciones funcionen
- **Estrategia**: Base de datos real (SQLite en memoria)
- **Velocidad**: Moderados
- **Casos de uso**:
  - Operaciones CRUD
  - Constraints de DB
  - Transacciones
  - Hashing de passwords

### Tests de Integración - Routes (integration/routes/)
- **Objetivo**: Verificar flujo HTTP completo
- **Estrategia**: Test client + DB real
- **Velocidad**: Más lentos (stack completo)
- **Casos de uso**:
  - Endpoints HTTP
  - Middlewares (auth, validación)
  - Códigos de estado
  - Flujos completos

## 🚀 Instalación

Instalar dependencias de testing:

```bash
pip install pytest pytest-flask pytest-cov --break-system-packages
```

## ▶️ Comandos de Ejecución

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar solo tests unitarios
```bash
pytest tests/unit/ -v
```

### Ejecutar solo tests de integración
```bash
pytest tests/integration/ -v
```

### Ejecutar tests de un módulo específico
```bash
pytest tests/unit/services/test_auth_service.py -v
```

### Ejecutar tests con marcadores
```bash
# Solo tests marcados como @pytest.mark.unit
pytest -m unit

# Solo tests marcados como @pytest.mark.integration
pytest -m integration

# Solo tests de autenticación
pytest -m auth
```

### Ejecutar un test específico
```bash
pytest tests/unit/services/test_auth_service.py::TestAuthServiceUnit::test_register_success -v
```

### Ver output detallado
```bash
pytest -v -s
```

### Ejecutar con coverage
```bash
# Generar reporte en terminal
pytest --cov=src --cov-report=term

# Generar reporte HTML
pytest --cov=src --cov-report=html

# Ver reporte HTML
open htmlcov/index.html
```

### Ejecutar tests en paralelo (más rápido)
```bash
pip install pytest-xdist --break-system-packages
pytest -n auto  # Usa todos los cores disponibles
```

## 📝 Patrones de Testing

### 1. Tests Unitarios - Service

```python
@pytest.mark.unit
class TestMyServiceUnit:
    
    def setup_method(self):
        self.my_service = MyService()
    
    @patch('src.services.my_service.execute_query')
    def test_my_method_success(self, mock_execute_query):
        # Arrange
        mock_execute_query.return_value = {
            'success': True,
            'data': {'id': 1}
        }
        
        # Act
        result = self.my_service.my_method()
        
        # Assert
        assert result['success'] is True
        mock_execute_query.assert_called_once()
```

### 2. Tests de Integración - Service

```python
@pytest.mark.integration
class TestMyServiceIntegration:
    
    def setup_method(self):
        self.my_service = MyService()
    
    def test_create_entity_in_database(self, session):
        # Arrange
        data = {'name': 'Test Entity'}
        
        # Act
        result = self.my_service.create_entity(data)
        
        # Assert
        assert result['success'] is True
        entity = session.query(Entity).first()
        assert entity.name == 'Test Entity'
```

### 3. Tests de Integración - Routes

```python
@pytest.mark.integration
class TestMyRoutes:
    
    def test_get_endpoint_success(self, client, auth_headers):
        # Act
        response = client.get(
            '/api/v1/my-endpoint',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
```

## 🔧 Fixtures Disponibles

### Fixtures Globales (conftest.py)
- `app`: Aplicación Flask configurada para testing
- `db`: Instancia de base de datos
- `session`: Sesión de DB con rollback automático
- `client`: Cliente HTTP para tests de endpoints
- `runner`: CLI runner

### Fixtures Unitarias (unit/conftest.py)
- `mock_db_session`: Mock de sesión de DB
- `mock_user`: Mock de modelo User
- `mock_login_attempt`: Mock de LoginAttempt
- `mock_execute_with_transaction`: Mock de función de transacciones
- `mock_execute_query`: Mock de función de queries
- `mock_generate_token`: Mock de generación de JWT
- `mock_logger`: Mock del logger
- `sample_user_data`: Datos de ejemplo para usuario
- `sample_login_data`: Datos de ejemplo para login

### Fixtures de Integración (integration/conftest.py)
- `create_user`: Factory para crear usuarios en DB
- `test_user`: Usuario de prueba pre-creado
- `admin_user`: Usuario admin pre-creado
- `inactive_user`: Usuario inactivo pre-creado
- `auth_token`: Token JWT válido
- `auth_headers`: Headers con Authorization
- `create_login_attempt`: Factory para crear intentos de login
- `sample_register_payload`: Payload de registro
- `sample_login_payload`: Payload de login
- `sample_update_profile_payload`: Payload de actualización
- `sample_change_password_payload`: Payload de cambio de contraseña

## 📊 Coverage

Para verificar la cobertura de código:

```bash
# Generar reporte
pytest --cov=src --cov-report=html --cov-report=term

# Ver estadísticas
pytest --cov=src --cov-report=term-missing
```

El reporte HTML se generará en `htmlcov/index.html` y mostrará:
- % de cobertura por módulo
- Líneas no cubiertas
- Branches no ejecutados

## 🎨 Mejores Prácticas

### 1. Nombrado de Tests
```python
# ✅ Bueno - descriptivo
def test_login_fails_with_invalid_password(self):
    pass

# ❌ Malo - ambiguo
def test_login_error(self):
    pass
```

### 2. Estructura AAA (Arrange-Act-Assert)
```python
def test_example(self):
    # Arrange - preparar datos
    user_data = {'email': 'test@example.com'}
    
    # Act - ejecutar acción
    result = service.create_user(user_data)
    
    # Assert - verificar resultado
    assert result['success'] is True
```

### 3. Un Assert por Concepto
```python
# ✅ Bueno
def test_user_creation(self):
    result = service.create_user(data)
    assert result['success'] is True
    assert result['data']['email'] == data['email']

# ⚠️ Evitar demasiados asserts no relacionados
```

### 4. Tests Independientes
```python
# ✅ Cada test debe poder ejecutarse solo
def test_login(self, session):
    user = create_user(session)  # Crear sus propios datos
    result = service.login(user.email, 'password')
    assert result['success'] is True

# ❌ No depender de estado de otros tests
```

### 5. Limpiar Estado
```python
# ✅ Usar fixtures con yield para cleanup
@pytest.fixture
def test_data(session):
    data = create_test_data()
    yield data
    cleanup_test_data(data)
```

## 🐛 Debugging Tests

### Ver print statements
```bash
pytest -s
```

### Parar en el primer error
```bash
pytest -x
```

### Ejecutar último test fallido
```bash
pytest --lf
```

### Ver traceback completo
```bash
pytest --tb=long
```

### Modo verbose máximo
```bash
pytest -vv
```

## 🔄 Replicar en Otros Módulos

Para agregar tests a un nuevo módulo (ej: `products`):

1. **Crear tests unitarios**:
   ```bash
   touch tests/unit/services/test_products_service.py
   ```

2. **Crear tests de integración de service**:
   ```bash
   touch tests/integration/services/test_products_service_db.py
   ```

3. **Crear tests de integración de routes**:
   ```bash
   touch tests/integration/routes/test_products_routes.py
   ```

4. **Agregar fixtures específicas** en los conftest.py correspondientes

5. **Seguir los patrones** de los tests de autenticación como template

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Flask Documentation](https://pytest-flask.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)

## ⚡ Tips

- Usa `-v` para ver nombres de tests mientras se ejecutan
- Usa `--lf` para re-ejecutar solo tests fallidos
- Usa `-x` para detener en el primer error
- Usa `-k "pattern"` para ejecutar tests que matcheen un patrón
- Usa `pytest --collect-only` para ver todos los tests sin ejecutarlos

## 🎯 Ejemplos de Comandos Comunes

```bash
# Desarrollo rápido - solo tests del módulo actual
pytest tests/unit/services/test_auth_service.py -v

# Pre-commit - ejecutar todos los tests rápidos
pytest tests/unit/ -v

# Pre-push - ejecutar todos los tests
pytest -v

# CI/CD - tests con coverage completo
pytest --cov=src --cov-report=xml --cov-report=term

# Debug de un test específico con prints
pytest tests/unit/services/test_auth_service.py::TestAuthServiceUnit::test_login_success -v -s
```