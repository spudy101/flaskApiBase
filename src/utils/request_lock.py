"""
Sistema de bloqueo de requests para prevenir duplicados
Equivalente a src/utils/requestLock.js
"""
import time
import threading
from typing import Optional, Dict

LOCK_TIMEOUT = 30000  # 30 segundos en milisegundos

class RequestLock:
    """
    Clase para manejar locks de requests
    Equivalente a createRequestLock() de Node.js
    """
    
    def __init__(self, timeout: int = LOCK_TIMEOUT):
        self.locks: Dict[str, float] = {}
        self.timeout = timeout / 1000  # Convertir a segundos
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._running = True
        
        # Iniciar limpieza periódica
        self._start_cleanup()
    
    def _start_cleanup(self):
        """Inicia el hilo de limpieza periódica"""
        def cleanup_worker():
            while self._running:
                time.sleep(60)  # Limpiar cada minuto
                self._cleanup()
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup(self):
        """Limpia locks expirados"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, lock_time in self.locks.items()
                if now - lock_time >= self.timeout
            ]
            for key in expired_keys:
                del self.locks[key]
    
    def acquire(self, key: Optional[str]) -> bool:
        """
        Intenta adquirir un lock para la key dada
        
        Args:
            key: Identificador único del lock
            
        Returns:
            bool: True si se adquirió el lock, False si ya existe
        """
        if not key:
            return True  # Permitir si no hay key
        
        with self._lock:
            now = time.time()
            lock_time = self.locks.get(key)
            
            # Verificar si existe un lock activo
            if lock_time and (now - lock_time) < self.timeout:
                return False
            
            # Adquirir el lock
            self.locks[key] = now
            return True
    
    def release(self, key: Optional[str]):
        """
        Libera un lock
        
        Args:
            key: Identificador único del lock
        """
        if key:
            with self._lock:
                self.locks.pop(key, None)
    
    def destroy(self):
        """Destruye el lock manager y limpia recursos"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=1)
        with self._lock:
            self.locks.clear()

def create_request_lock(timeout: int = LOCK_TIMEOUT) -> RequestLock:
    """
    Factory para crear un RequestLock
    Equivalente a createRequestLock() de Node.js
    
    Args:
        timeout: Tiempo de expiración del lock en milisegundos
        
    Returns:
        RequestLock: Instancia del lock manager
    """
    return RequestLock(timeout)

__all__ = ['RequestLock', 'create_request_lock', 'LOCK_TIMEOUT']
