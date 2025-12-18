"""
Tests unitarios para crypto_utils
"""
import pytest
from src.utils.crypto_utils import encriptar_mensaje, desencriptar_mensaje, generar_token

class TestCryptoUtils:
    """Tests para utilidades de criptografía"""
    
    class TestEncriptarMensaje:
        """Tests para encriptar_mensaje"""
        
        def test_encripta_mensaje_correctamente(self):
            """Debería encriptar un mensaje correctamente"""
            mensaje = "mensaje secreto"
            encrypted = encriptar_mensaje(mensaje)
            
            assert encrypted is not None
            assert isinstance(encrypted, str)
            assert encrypted != mensaje
            assert len(encrypted) > 0
        
        def test_genera_mismo_valor_con_iv_fijo(self):
            """Con IV fijo, debería generar el mismo valor para el mismo mensaje"""
            mensaje = "test"
            encrypted1 = encriptar_mensaje(mensaje)
            encrypted2 = encriptar_mensaje(mensaje)
            
            assert encrypted1 == encrypted2
        
        def test_maneja_strings_vacios(self):
            """Debería manejar strings vacíos"""
            encrypted = encriptar_mensaje("")
            assert encrypted is not None
            assert isinstance(encrypted, str)
        
        def test_maneja_caracteres_especiales(self):
            """Debería manejar caracteres especiales"""
            mensaje = "ñáéíóú@#$%&*()"
            encrypted = encriptar_mensaje(mensaje)
            
            assert encrypted is not None
            assert isinstance(encrypted, str)
        
        def test_maneja_unicode(self):
            """Debería manejar caracteres unicode"""
            mensaje = "🔐 Mensaje con emoji 🚀"
            encrypted = encriptar_mensaje(mensaje)
            
            assert encrypted is not None
            assert isinstance(encrypted, str)
    
    class TestDesencriptarMensaje:
        """Tests para desencriptar_mensaje"""
        
        def test_desencripta_correctamente(self):
            """Debería desencriptar un mensaje correctamente"""
            original = "mensaje secreto"
            encrypted = encriptar_mensaje(original)
            decrypted = desencriptar_mensaje(encrypted)
            
            assert decrypted == original
        
        def test_desencripta_strings_vacios(self):
            """Debería desencriptar strings vacíos"""
            original = ""
            encrypted = encriptar_mensaje(original)
            decrypted = desencriptar_mensaje(encrypted)
            
            assert decrypted == original
        
        def test_desencripta_caracteres_especiales(self):
            """Debería desencriptar caracteres especiales"""
            original = "ñáéíóú@#$%&*()"
            encrypted = encriptar_mensaje(original)
            decrypted = desencriptar_mensaje(encrypted)
            
            assert decrypted == original
        
        def test_lanza_error_con_datos_invalidos(self):
            """Debería lanzar error con datos corruptos"""
            with pytest.raises(Exception):
                desencriptar_mensaje("datos-invalidos")
        
        def test_maneja_numeros_como_strings(self):
            """Debería manejar números encriptados como strings"""
            import time
            timestamp = str(int(time.time() * 1000))
            encrypted = encriptar_mensaje(timestamp)
            decrypted = desencriptar_mensaje(encrypted)
            
            assert decrypted == timestamp
            assert int(decrypted) == int(timestamp)
    
    class TestGenerarToken:
        """Tests para generar_token"""
        
        def test_genera_token_longitud_correcta(self):
            """Debería generar un token de longitud correcta"""
            token = generar_token(64)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) == 128  # 64 bytes = 128 caracteres hex
        
        def test_genera_tokens_unicos(self):
            """Debería generar tokens únicos"""
            token1 = generar_token()
            token2 = generar_token()
            
            assert token1 != token2
        
        def test_genera_token_longitud_personalizada(self):
            """Debería generar token con longitud personalizada"""
            token = generar_token(32)
            assert len(token) == 64  # 32 bytes = 64 caracteres hex
        
        def test_genera_solo_caracteres_hexadecimales(self):
            """Debería generar solo caracteres hexadecimales"""
            import re
            token = generar_token()
            hex_regex = re.compile(r'^[0-9a-f]+$')
            assert hex_regex.match(token) is not None
    
    class TestIntegracion:
        """Tests de integración encriptar/desencriptar"""
        
        def test_mantiene_integridad_con_multiples_ciclos(self):
            """Debería mantener integridad de datos con múltiples ciclos"""
            original = "datos importantes"
            encrypted = encriptar_mensaje(original)
            
            for _ in range(5):
                decrypted = desencriptar_mensaje(encrypted)
                assert decrypted == original
                encrypted = encriptar_mensaje(decrypted)
        
        def test_maneja_strings_largos(self):
            """Debería manejar strings largos"""
            original = "a" * 10000
            encrypted = encriptar_mensaje(original)
            decrypted = desencriptar_mensaje(encrypted)
            
            assert decrypted == original
            assert len(decrypted) == 10000
        
        def test_diferentes_mensajes_diferentes_resultados(self):
            """Mensajes diferentes deberían producir encriptaciones diferentes"""
            encrypted1 = encriptar_mensaje("mensaje1")
            encrypted2 = encriptar_mensaje("mensaje2")
            
            assert encrypted1 != encrypted2
