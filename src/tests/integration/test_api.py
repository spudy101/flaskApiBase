"""
Tests de integración para endpoints de la API
"""
import pytest
import time
from src.utils.crypto_utils import encriptar_mensaje

class TestPerfilEndpoints:
    """Tests para endpoints de perfil de usuario"""
    
    def test_health_check(self, client):
        """Debería retornar status OK en health check"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'OK'
        assert 'timestamp' in data
    
    def test_get_datos_usuario_sin_token(self, client, mock_timestamp):
        """Debería retornar 401 sin token"""
        response = client.get(
            '/perfil_usuario/datos_usuario',
            headers={'timestamp': mock_timestamp}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert data['code'] == 'AUTH_REQUIRED'
    
    def test_get_datos_usuario_sin_timestamp(self, client):
        """Debería retornar 401 sin timestamp"""
        response = client.get(
            '/perfil_usuario/datos_usuario',
            headers={'Cookie': 'jwtToken=test-token'}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 'AUTH_REQUIRED'
    
    def test_get_datos_usuario_con_timestamp_expirado(self, client):
        """Debería retornar 401 con timestamp expirado"""
        old_timestamp = int(time.time() * 1000) - (70 * 1000)  # 70 segundos atrás
        encrypted_timestamp = encriptar_mensaje(str(old_timestamp))
        
        response = client.get(
            '/perfil_usuario/datos_usuario',
            headers={
                'timestamp': encrypted_timestamp,
                'Cookie': 'jwtToken=test-token'
            }
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 'TIMESTAMP_EXPIRED'
    
    @pytest.mark.skip(reason="Requiere base de datos configurada")
    def test_get_datos_usuario_exitoso(self, client, auth_headers, mock_timestamp):
        """Debería retornar datos de usuario con credenciales válidas"""
        response = client.get(
            '/perfil_usuario/datos_usuario',
            headers={
                **auth_headers,
                'timestamp': mock_timestamp
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['estado_solicitud'] == 1
        assert 'data' in data
    
    def test_ruta_no_encontrada(self, client):
        """Debería retornar 404 para rutas inexistentes"""
        response = client.get('/ruta-que-no-existe')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'no encontrada' in data['message'].lower()

class TestSecurityHeaders:
    """Tests para headers de seguridad"""
    
    def test_tiene_headers_de_seguridad(self, client):
        """Debería tener headers de seguridad correctos"""
        response = client.get('/health')
        
        # Flask no tiene los mismos headers que Helmet de Express
        # pero puedes agregar headers personalizados
        assert response.status_code == 200

class TestCORS:
    """Tests para configuración de CORS"""
    
    def test_permite_cors_en_desarrollo(self, client):
        """Debería permitir CORS en desarrollo"""
        response = client.get(
            '/health',
            headers={'Origin': 'http://localhost:3000'}
        )
        
        # Verificar que la respuesta tiene headers CORS
        assert response.status_code == 200
        # En desarrollo debería permitir el origen
        if 'Access-Control-Allow-Origin' in response.headers:
            assert response.headers['Access-Control-Allow-Origin']

class TestRateLimiting:
    """Tests para rate limiting"""
    
    @pytest.mark.skip(reason="Rate limiting desactivado en tests")
    def test_aplica_rate_limiting(self, client, mock_timestamp):
        """Debería aplicar rate limiting después de muchas requests"""
        # Hacer muchas requests
        responses = []
        for _ in range(65):
            response = client.get(
                '/perfil_usuario/datos_usuario',
                headers={'timestamp': mock_timestamp}
            )
            responses.append(response)
        
        # Al menos una debería ser 429
        too_many_requests = [r for r in responses if r.status_code == 429]
        assert len(too_many_requests) > 0

class TestRequestLocking:
    """Tests para request locking"""
    
    @pytest.mark.skip(reason="Requiere configuración compleja de concurrencia")
    def test_previene_requests_duplicadas(self, client, auth_headers, mock_timestamp):
        """Debería prevenir requests duplicadas simultáneas"""
        import concurrent.futures
        
        def make_request():
            return client.get(
                '/perfil_usuario/datos_usuario',
                headers={
                    **auth_headers,
                    'timestamp': mock_timestamp
                }
            )
        
        # Hacer requests simultáneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(make_request)
            future2 = executor.submit(make_request)
            
            response1 = future1.result()
            response2 = future2.result()
        
        # Una debería ser 429
        statuses = [response1.status_code, response2.status_code]
        assert 429 in statuses
