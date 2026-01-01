"""
Redis Utility - Redis client wrapper
Equivalente a src/utils/redis.js
"""
import redis
import os
from typing import Optional, Any
import json
from src.utils.logger_util import logger


class RedisUtil:
    """
    Redis client wrapper
    Equivalente a RedisClient en Node.js
    """
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Conecta a Redis"""
        try:
            redis_url = os.getenv('REDIS_URL')
            
            if redis_url:
                # Usar URL completa
                self._client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
            else:
                # Configuración individual
                self._client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    password=os.getenv('REDIS_PASSWORD', None),
                    db=int(os.getenv('REDIS_DB', 0)),
                    decode_responses=True,
                    socket_connect_timeout=5
                )
            
            # Test connection
            self._client.ping()
            logger.info('✅ Redis connected successfully')
            
        except Exception as e:
            logger.warning(f'⚠️  Redis connection failed: {e}. Running without cache.')
            self._client = None
    
    def get_client(self) -> Optional[redis.Redis]:
        """Retorna cliente Redis"""
        return self._client
    
    def is_connected(self) -> bool:
        """Verifica si está conectado"""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Establece un valor en Redis
        
        Args:
            key: Key
            value: Valor (se serializa a JSON si no es string)
            ttl: Time to live en segundos
        """
        if not self._client:
            return False
        
        try:
            # Serializar a JSON si no es string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            if ttl:
                self._client.setex(key, ttl, value)
            else:
                self._client.set(key, value)
            
            return True
        except Exception as e:
            logger.error(f'Redis SET error: {e}', key=key)
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor de Redis
        
        Args:
            key: Key
            
        Returns:
            Value (deserializado de JSON si es posible)
        """
        if not self._client:
            return None
        
        try:
            value = self._client.get(key)
            
            if value is None:
                return None
            
            # Intentar deserializar JSON
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logger.error(f'Redis GET error: {e}', key=key)
            return None
    
    def delete(self, key: str) -> bool:
        """Elimina una key de Redis"""
        if not self._client:
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f'Redis DELETE error: {e}', key=key)
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si existe una key"""
        if not self._client:
            return False
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f'Redis EXISTS error: {e}', key=key)
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa un contador"""
        if not self._client:
            return None
        
        try:
            return self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f'Redis INCR error: {e}', key=key)
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Establece TTL en una key existente"""
        if not self._client:
            return False
        
        try:
            return bool(self._client.expire(key, ttl))
        except Exception as e:
            logger.error(f'Redis EXPIRE error: {e}', key=key)
            return False


# Singleton instance
redis_util = RedisUtil()
