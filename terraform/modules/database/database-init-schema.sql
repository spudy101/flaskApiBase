-- ============================================================================
-- PostgreSQL Schema Initialization
-- ============================================================================
-- Este script crea el schema 'app_schema' y configura permisos básicos.
-- Se ejecuta una sola vez después de crear la base de datos RDS.
--
-- Ejecución manual:
-- PGPASSWORD=your_password psql -h your-rds-endpoint.rds.amazonaws.com \
--   -U postgres -d nodejsapidb -f init-schema.sql
-- ============================================================================

-- Crear schema si no existe
CREATE SCHEMA IF NOT EXISTS app_schema;

-- Otorgar permisos al usuario postgres
GRANT ALL PRIVILEGES ON SCHEMA app_schema TO postgres;

-- Configurar search_path por defecto
ALTER DATABASE nodejsapidb SET search_path TO app_schema, public;

-- Habilitar extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA app_schema;
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" SCHEMA public;

-- Verificación
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'app_schema';

-- Mensaje de éxito
DO $$
BEGIN
  RAISE NOTICE 'Schema app_schema creado exitosamente';
END $$;
