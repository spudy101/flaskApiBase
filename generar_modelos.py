import os
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print('🚀 Iniciando generación de modelos...')
print(f'📊 Base de datos: {os.getenv("DB_NAME")}@{os.getenv("DB_HOST")}')

# Construir la URI de conexión
db_dialect = os.getenv('DB_DIALECT', 'mysql').lower()
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', 3306 if db_dialect == 'mysql' else 5432)
db_name = os.getenv('DB_NAME')

if db_dialect == 'mysql':
    database_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
elif db_dialect == 'postgresql':
    database_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
    print(f'❌ Dialecto de base de datos no soportado: {db_dialect}')
    exit(1)

# Directorio de salida
output_dir = 'src/models'
output_file = f'{output_dir}/generated_models.py'

# Crear directorio si no existe
os.makedirs(output_dir, exist_ok=True)

print(f'📁 Generando modelos en: {output_file}')

# Comando de sqlacodegen
# Instalación: pip install sqlacodegen
try:
    # Generar modelos con sqlacodegen
    cmd = [
        'sqlacodegen',
        database_uri,
        '--outfile', output_file,
        '--noviews',  # No generar vistas
        '--noindexes',  # Opcional: no incluir índices
    ]
    
    # Tablas a excluir (opcional)
    excluded_tables = ['migrations', 'seeders', 'sessions']
    for table in excluded_tables:
        cmd.extend(['--tables', f'!{table}'])
    
    print('🔄 Ejecutando sqlacodegen...')
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print('✅ Modelos generados exitosamente!')
        print(f'📄 Archivo creado: {output_file}')
        
        # Crear __init__.py para importar modelos fácilmente
        init_file = f'{output_dir}/__init__.py'
        with open(init_file, 'w') as f:
            f.write('"""\n')
            f.write('Módulo de modelos\n')
            f.write('Modelos generados automáticamente desde la base de datos\n')
            f.write('"""\n')
            f.write('from .generated_models import *\n')
        
        print(f'📄 Archivo creado: {init_file}')
        print('\n🎉 ¡Generación completada!')
        print('💡 Importa tus modelos con: from src.models import Usuario, Persona, etc.')
        print('\n⚠️  NOTA: Revisa los modelos generados y ajusta si es necesario')
        print('   - Verifica las relaciones (relationships)')
        print('   - Ajusta nombres de tablas si es necesario')
        print('   - Agrega validaciones personalizadas')
    else:
        print('❌ Error al generar modelos:')
        print(result.stderr)
        print('\n💡 Asegúrate de tener sqlacodegen instalado:')
        print('   pip install sqlacodegen')
        exit(1)
        
except FileNotFoundError:
    print('❌ sqlacodegen no está instalado')
    print('💡 Instálalo con: pip install sqlacodegen')
    print('💡 Para PostgreSQL también necesitas: pip install psycopg2-binary')
    print('💡 Para MySQL también necesitas: pip install pymysql')
    exit(1)
except Exception as e:
    print(f'❌ Error inesperado: {str(e)}')
    exit(1)
