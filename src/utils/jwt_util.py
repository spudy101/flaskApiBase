"""
JWT Utility - Token generation and verification
Equivalente a src/utils/jwt.js
"""
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os


class JWTUtil:
    """
    JWT Utility class
    Equivalente a JWTUtil en Node.js
    """
    
    # Secrets desde environment variables
    ACCESS_SECRET = os.getenv('JWT_ACCESS_SECRET', 'dev-access-secret-change-me')
    REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET', 'dev-refresh-secret-change-me')
    
    # Token expiry
    ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)
    REFRESH_TOKEN_EXPIRY = timedelta(days=7)
    
    # Algorithm
    ALGORITHM = 'HS256'
    
    @classmethod
    def generate_access_token(cls, user) -> str:
        """
        Genera access token
        Equivalente a generateAccessToken() en Node.js
        """
        payload = {
            'id': user.id,
            'email': user.email,
            'role': user.role.value if hasattr(user.role, 'value') else user.role,
            'exp': datetime.utcnow() + cls.ACCESS_TOKEN_EXPIRY,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, cls.ACCESS_SECRET, algorithm=cls.ALGORITHM)
    
    @classmethod
    def generate_refresh_token(cls, user) -> str:
        """
        Genera refresh token
        Equivalente a generateRefreshToken() en Node.js
        """
        payload = {
            'id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + cls.REFRESH_TOKEN_EXPIRY,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, cls.REFRESH_SECRET, algorithm=cls.ALGORITHM)
    
    @classmethod
    def generate_token_pair(cls, user) -> Dict[str, str]:
        """
        Genera par de tokens (access + refresh)
        Equivalente a generateTokenPair() en Node.js
        """
        return {
            'access_token': cls.generate_access_token(user),
            'refresh_token': cls.generate_refresh_token(user)
        }
    
    @classmethod
    def verify_access_token(cls, token: str) -> Dict[str, Any]:
        """
        Verifica access token
        Equivalente a verifyAccessToken() en Node.js
        
        Raises:
            jwt.ExpiredSignatureError: Token expirado
            jwt.InvalidTokenError: Token inválido
        """
        try:
            payload = jwt.decode(token, cls.ACCESS_SECRET, algorithms=[cls.ALGORITHM])
            
            # Verificar que sea access token
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError('Not an access token')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise
    
    @classmethod
    def verify_refresh_token(cls, token: str) -> Dict[str, Any]:
        """
        Verifica refresh token
        Equivalente a verifyRefreshToken() en Node.js
        
        Raises:
            jwt.ExpiredSignatureError: Token expirado
            jwt.InvalidTokenError: Token inválido
        """
        try:
            payload = jwt.decode(token, cls.REFRESH_SECRET, algorithms=[cls.ALGORITHM])
            
            # Verificar que sea refresh token
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError('Not a refresh token')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise
    
    @classmethod
    def decode_token(cls, token: str, verify: bool = False) -> Optional[Dict[str, Any]]:
        """
        Decodifica token sin verificar (útil para debugging)
        Equivalente a decode() en Node.js
        """
        try:
            options = {'verify_signature': verify, 'verify_exp': verify}
            return jwt.decode(token, options=options, algorithms=[cls.ALGORITHM])
        except Exception:
            return None


# Singleton instance
jwt_util = JWTUtil()
