#!/bin/bash

# Scripts útiles para el proyecto Flask

show_help() {
    echo "🚀 Flask API Base - Scripts de Utilidad"
    echo ""
    echo "Uso: ./run.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup          - Configuración inicial completa"
    echo "  install        - Instalar dependencias"
    echo "  dev            - Ejecutar en modo desarrollo"
    echo "  prod           - Ejecutar en modo producción"
    echo "  generate       - Generar modelos desde BD"
    echo "  test           - Ejecutar tests"
    echo "  lint           - Revisar código con flake8"
    echo "  format         - Formatear código con black"
    echo "  docker-build   - Construir imagen Docker"
    echo "  docker-run     - Ejecutar en Docker"
    echo "  clean          - Limpiar archivos temporales"
    echo ""
}

setup() {
    echo "🔧 Configuración inicial..."
    
    # Crear entorno virtual
    if [ ! -d "venv" ]; then
        echo "📦 Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    # Activar entorno
    source venv/bin/activate
    
    # Instalar dependencias
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
    
    # Copiar .env si no existe
    if [ ! -f ".env" ]; then
        echo "📝 Copiando .env.example a .env..."
        cp .env.example .env
        echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales"
    fi
    
    echo "✅ Configuración completada!"
    echo "💡 Próximos pasos:"
    echo "   1. Edita el archivo .env con tus credenciales"
    echo "   2. Ejecuta: ./run.sh generate (para generar modelos)"
    echo "   3. Ejecuta: ./run.sh dev (para iniciar el servidor)"
}

install() {
    echo "📥 Instalando dependencias..."
    source venv/bin/activate 2>/dev/null || true
    pip install -r requirements.txt
    echo "✅ Dependencias instaladas!"
}

dev() {
    echo "🚀 Iniciando servidor en modo desarrollo..."
    source venv/bin/activate 2>/dev/null || true
    export FLASK_ENV=development
    export FLASK_DEBUG=True
    python index.py
}

prod() {
    echo "🚀 Iniciando servidor en modo producción..."
    source venv/bin/activate 2>/dev/null || true
    export FLASK_ENV=production
    gunicorn -w 4 -b 0.0.0.0:5000 "src.app:create_app()"
}

generate() {
    echo "🔄 Generando modelos desde la base de datos..."
    source venv/bin/activate 2>/dev/null || true
    
    # Instalar sqlacodegen si no está instalado
    pip install sqlacodegen 2>/dev/null || true
    
    python generar_modelos.py
    echo "✅ Modelos generados!"
}

run_tests() {
    echo "🧪 Ejecutando tests..."
    source venv/bin/activate 2>/dev/null || true
    pytest
}

lint() {
    echo "🔍 Revisando código con flake8..."
    source venv/bin/activate 2>/dev/null || true
    flake8 src/ --max-line-length=120 --exclude=venv,__pycache__
}

format_code() {
    echo "✨ Formateando código con black..."
    source venv/bin/activate 2>/dev/null || true
    black src/ --line-length=120
}

docker_build() {
    echo "🐳 Construyendo imagen Docker..."
    docker build -t flask-api-base .
    echo "✅ Imagen construida!"
}

docker_run() {
    echo "🐳 Ejecutando en Docker..."
    docker run -p 5000:5000 --env-file .env flask-api-base
}

clean() {
    echo "🧹 Limpiando archivos temporales..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache 2>/dev/null || true
    echo "✅ Limpieza completada!"
}

# Main
case "$1" in
    setup)
        setup
        ;;
    install)
        install
        ;;
    dev)
        dev
        ;;
    prod)
        prod
        ;;
    generate)
        generate
        ;;
    test)
        run_tests
        ;;
    lint)
        lint
        ;;
    format)
        format_code
        ;;
    docker-build)
        docker_build
        ;;
    docker-run)
        docker_run
        ;;
    clean)
        clean
        ;;
    *)
        show_help
        ;;
esac
