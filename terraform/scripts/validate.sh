#!/bin/bash
# ============================================================================
# Script de Validación de Terraform
# ============================================================================
# Este script valida la configuración de Terraform antes de aplicarla
# Uso: ./scripts/validate.sh <environment>
# Ejemplo: ./scripts/validate.sh dev
# ============================================================================

set -e

ENVIRONMENT=$1

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${NC}ℹ${NC} $1"
}

# Validar parámetros
if [ -z "$ENVIRONMENT" ]; then
    print_error "Debes especificar un ambiente: dev, staging, o prod"
    echo "Uso: ./scripts/validate.sh <environment>"
    exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Ambiente inválido: $ENVIRONMENT"
    echo "Ambientes válidos: dev, staging, prod"
    exit 1
fi

echo "=================================================="
echo "  Validando Terraform para ambiente: $ENVIRONMENT"
echo "=================================================="
echo ""

# 1. Verificar que Terraform está instalado
print_info "1. Verificando Terraform..."
if command -v terraform &> /dev/null; then
    TERRAFORM_VERSION=$(terraform version | head -n 1)
    print_success "Terraform instalado: $TERRAFORM_VERSION"
else
    print_error "Terraform no está instalado"
    exit 1
fi

# 2. Verificar AWS CLI
print_info "2. Verificando AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    print_success "AWS CLI instalado: $AWS_VERSION"
else
    print_error "AWS CLI no está instalado"
    exit 1
fi

# 3. Verificar credenciales AWS
print_info "3. Verificando credenciales AWS..."
if aws sts get-caller-identity &> /dev/null; then
    AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    AWS_USER=$(aws sts get-caller-identity --query Arn --output text)
    print_success "Credenciales válidas"
    echo "   Account ID: $AWS_ACCOUNT"
    echo "   User: $AWS_USER"
else
    print_error "Credenciales AWS no válidas o no configuradas"
    exit 1
fi

# 4. Verificar que existe terraform.tfvars
print_info "4. Verificando terraform.tfvars..."
TFVARS_FILE="environments/$ENVIRONMENT/terraform.tfvars"
if [ -f "$TFVARS_FILE" ]; then
    print_success "Archivo $TFVARS_FILE existe"
else
    print_error "Archivo $TFVARS_FILE no existe"
    echo "   Crea el archivo desde: environments/$ENVIRONMENT/terraform.tfvars.example"
    exit 1
fi

# 5. Verificar que no tiene valores de ejemplo
print_info "5. Verificando que no hay valores de ejemplo..."
if grep -q "CAMBIAR" "$TFVARS_FILE" 2>/dev/null; then
    print_warning "El archivo contiene valores 'CAMBIAR' que deben ser actualizados"
    grep "CAMBIAR" "$TFVARS_FILE" | head -n 3
    echo ""
fi

if grep -q "GENERAR_CON" "$TFVARS_FILE" 2>/dev/null; then
    print_warning "El archivo contiene valores 'GENERAR_CON' que deben ser reemplazados"
    grep "GENERAR_CON" "$TFVARS_FILE" | head -n 3
    echo ""
fi

# 6. Verificar backend.hcl
print_info "6. Verificando backend.hcl..."
BACKEND_FILE="environments/$ENVIRONMENT/backend.hcl"
if [ -f "$BACKEND_FILE" ]; then
    print_success "Archivo $BACKEND_FILE existe"
else
    print_error "Archivo $BACKEND_FILE no existe"
    exit 1
fi

# 7. Verificar S3 bucket para state
print_info "7. Verificando S3 bucket para Terraform state..."
BUCKET_NAME=$(grep "bucket" "$BACKEND_FILE" | awk '{print $3}' | tr -d '"')
if aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    print_success "Bucket $BUCKET_NAME existe y es accesible"
else
    print_error "Bucket $BUCKET_NAME no existe o no es accesible"
    echo "   Ejecuta el bootstrapping primero (ver README)"
    exit 1
fi

# 8. Verificar DynamoDB table para locks
print_info "8. Verificando DynamoDB table para locks..."
TABLE_NAME=$(grep "dynamodb_table" "$BACKEND_FILE" | awk '{print $3}' | tr -d '"')
if aws dynamodb describe-table --table-name "$TABLE_NAME" &> /dev/null; then
    print_success "Tabla $TABLE_NAME existe"
else
    print_error "Tabla $TABLE_NAME no existe"
    echo "   Ejecuta el bootstrapping primero (ver README)"
    exit 1
fi

# 9. Verificar formato de archivos .tf
print_info "9. Verificando formato de archivos Terraform..."
if terraform fmt -check -recursive &> /dev/null; then
    print_success "Archivos formateados correctamente"
else
    print_warning "Algunos archivos necesitan formateo"
    echo "   Ejecuta: terraform fmt -recursive"
fi

# 10. Validar sintaxis
print_info "10. Validando sintaxis de Terraform..."
if terraform validate &> /dev/null; then
    print_success "Sintaxis válida"
else
    print_error "Errores de sintaxis encontrados"
    terraform validate
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Validación completada exitosamente${NC}"
echo "=================================================="
echo ""
echo "Siguiente paso:"
echo "  terraform init -backend-config=$BACKEND_FILE"
echo "  terraform plan -var-file=$TFVARS_FILE"
echo ""
