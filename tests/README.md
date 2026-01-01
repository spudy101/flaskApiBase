# 🧪 TESTS - FLASK API

## 📁 Estructura

```
tests/
├── conftest.py                    # Configuración global de pytest
├── pytest.ini                     # Configuración de pytest
├── fixtures/
│   ├── __init__.py
│   └── fixtures.py                # Fixtures reutilizables
│
├── unit/                          # Tests unitarios (sin DB)
│   ├── dto/
│   │   └── test_auth_dto.py      # ✅ 15 tests - DTOs
│   └── services/
│       └── test_auth_service.py  # ✅ 18 tests - Services con mocks
│
└── integration/                   # Tests de integración (con DB)
    └── api/
        └── test_auth_api.py      # ✅ 29 tests - API endpoints
```

## 🚀 Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Solo unit tests (rápidos)
```bash
pytest tests/unit/ -v
```

### Solo integration tests
```bash
pytest tests/integration/ -v
```

### Con coverage
```bash
pytest --cov=src --cov-report=html
```

### Un archivo específico
```bash
pytest tests/unit/dto/test_auth_dto.py -v
```

### Watch mode (con pytest-watch)
```bash
pip install pytest-watch
ptw
```

## 📊 Tests Creados

### ✅ DTO Tests (15 tests)
**test_auth_dto.py:**
- RegisterDTO: from_request, defaults, sanitización
- LoginDTO: from_request, email lowercase
- RefreshTokenDTO: snake_case y camelCase support
- UserResponseDTO: from_model, to_dict, exclude None
- TokensDTO: creation, to_dict
- AuthResponseDTO: from_data, nested structure

### ✅ Service Tests (18 tests)
**test_auth_service.py:**
- register(): éxito, email duplicado
- login(): éxito, bloqueado, credenciales inválidas, password incorrecto
- logout(): éxito
- refresh_token(): éxito, token expirado
- verify_token(): token válido, token expirado

### ✅ API Integration Tests (29 tests)
**test_auth_api.py:**
- POST /api/auth/register: éxito, email duplicado, validaciones
- POST /api/auth/login: éxito, email inválido, password incorrecto, bloqueo
- POST /api/auth/logout: éxito, sin token
- POST /api/auth/refresh: éxito, token inválido
- GET /api/auth/me: éxito, sin auth
- GET /api/auth/verify: token válido, token inválido

**Total: 62 test cases**

## 🛠️ Fixtures Disponibles

```python
# En tests/fixtures/fixtures.py

mock_user                  # Mock user para unit tests
sample_register_data       # Datos de registro
sample_login_data          # Datos de login
sample_product_data        # Datos de producto
create_test_user()         # Helper para crear usuario en DB
create_test_product()      # Helper para crear producto en DB
auth_headers()             # Helper para headers con JWT
```

## 📝 Convenciones

### Naming
```python
# Archivos: test_*.py
# Classes: TestNombreDelModulo
# Methods: test_descripcion_del_caso
```

### Estructura AAA
```python
def test_example():
    # Arrange
    data = {...}
    
    # Act
    result = function(data)
    
    # Assert
    assert result == expected
```

### Mocking
```python
@patch('src.services.auth_service.user_repository')
def test_with_mock(self, mock_repo):
    mock_repo.find_by_email.return_value = None
    # ...
```

## ⚙️ Configuración

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short
```

### conftest.py
Provee fixtures globales:
- `app`: Flask app configurada para testing
- `db`: Database con estructura creada
- `session`: DB session con rollback automático
- `client`: Test client para requests HTTP

## 🎯 Coverage Esperado

```
src/dto/         100%
src/utils/       85%
src/services/    90%
src/controllers/ 85%
src/models/      90%
Global:          85%+
```

## 🔧 Troubleshooting

### Tests fallan: "No such table"
```bash
# Asegúrate de que app.config usa 'test'
pytest tests/ -v --log-cli-level=DEBUG
```

### Mocks no funcionan
```python
# Usar path completo en @patch
@patch('src.services.auth_service.user_repository')  # ✅
@patch('user_repository')  # ❌
```

### DB no se limpia
```python
# El conftest.py ya tiene rollback automático
# Si necesitas limpiar manualmente:
db.session.rollback()
```

## 📚 Recursos

- [Pytest Docs](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
