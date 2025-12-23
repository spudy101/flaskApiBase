#!/usr/bin/env python3
"""
Script para generar claves de encriptación seguras
Ejecutar: python generate_encryption_key.py
"""

import secrets

def main():
    print('\n🔐 Generando clave de encriptación segura...\n')
    
    # Generar clave aleatoria de 32 bytes (256 bits)
    key = secrets.token_hex(32)
    
    print('Copia esta clave a tu archivo .env:')
    print('=' * 70)
    print(f'ENCRYPTION_KEY={key}')
    print('=' * 70)
    print()
    
    print('⚠️  IMPORTANTE:')
    print('- Nunca compartas esta clave')
    print('- Usa una clave diferente en cada ambiente (dev, staging, prod)')
    print('- Si cambias la clave, los datos encriptados anteriores no podrán desencriptarse')
    print('- Guarda esta clave en un lugar seguro (gestores de secretos en producción)')
    print()


if __name__ == '__main__':
    main()