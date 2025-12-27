#!/bin/bash
# ============================================================================
# Script de Despliegue de Terraform
# ============================================================================
# Este script automatiza el despliegue de infraestructura
# Uso: ./scripts/deploy.sh <environment> [plan|apply|destroy]
# Ejemplo: ./scripts/deploy.sh dev apply
# ============================================================================

set -e

ENVIRONMENT=$1
ACTION=${2:-plan}

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Validar parámetros
if [ -z "$ENVIRONMENT" ]; then
    print_error "Debes especificar un ambiente"
    echo "Uso: ./scripts/deploy.sh <environment> [plan|apply|destroy]"
    exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Ambiente inválido: $ENVIRONMENT"
    exit 1
fi

if [[ ! "$ACTION" =~ ^(plan|apply|destroy)$ ]]; then
    print_error "Acción inválida: $ACTION"
    echo "Acciones válidas: plan, apply, destroy"
    exit 1
fi

BACKEND_FILE="environments/$ENVIRONMENT/backend.hcl"
TFVARS_FILE="environments/$ENVIRONMENT/terraform.tfvars"

echo "=================================================="
echo "  Terraform Deployment"
echo "=================================================="
echo "  Environment: $ENVIRONMENT"
echo "  Action: $ACTION"
echo "=================================================="
echo ""

# Confirmar destrucción en prod
if [ "$ACTION" == "destroy" ] && [ "$ENVIRONMENT" == "prod" ]; then
    print_warning "¡ADVERTENCIA! Estás a punto de DESTRUIR el ambiente de PRODUCCIÓN"
    read -p "Escribe 'DESTROY PRODUCTION' para confirmar: " CONFIRM
    if [ "$CONFIRM" != "DESTROY PRODUCTION" ]; then
        print_error "Destrucción cancelada"
        exit 1
    fi
fi

# 1. Inicializar Terraform
print_info "Inicializando Terraform..."
terraform init -backend-config="$BACKEND_FILE" -reconfigure

# 2. Validar configuración
print_info "Validando configuración..."
terraform validate

# 3. Formatear archivos
print_info "Formateando archivos..."
terraform fmt -recursive

# 4. Ejecutar acción
case $ACTION in
    plan)
        print_info "Generando plan..."
        terraform plan -var-file="$TFVARS_FILE" -out=tfplan
        print_success "Plan generado exitosamente"
        echo ""
        print_info "Para aplicar este plan ejecuta:"
        echo "  terraform apply tfplan"
        ;;
    
    apply)
        print_info "Generando plan..."
        terraform plan -var-file="$TFVARS_FILE" -out=tfplan
        
        echo ""
        print_warning "¿Continuar con el apply?"
        read -p "Escribe 'yes' para confirmar: " CONFIRM
        
        if [ "$CONFIRM" == "yes" ]; then
            print_info "Aplicando cambios..."
            terraform apply tfplan
            rm -f tfplan
            print_success "Infraestructura desplegada exitosamente"
            
            echo ""
            print_info "Outputs importantes:"
            terraform output
        else
            print_warning "Apply cancelado"
            rm -f tfplan
            exit 0
        fi
        ;;
    
    destroy)
        print_warning "Generando plan de destrucción..."
        terraform plan -destroy -var-file="$TFVARS_FILE"
        
        echo ""
        print_warning "¿Continuar con la destrucción?"
        read -p "Escribe 'yes' para confirmar: " CONFIRM
        
        if [ "$CONFIRM" == "yes" ]; then
            print_info "Destruyendo infraestructura..."
            terraform destroy -var-file="$TFVARS_FILE" -auto-approve
            print_success "Infraestructura destruida"
        else
            print_warning "Destrucción cancelada"
            exit 0
        fi
        ;;
esac

echo ""
echo "=================================================="
print_success "Operación completada"
echo "=================================================="
