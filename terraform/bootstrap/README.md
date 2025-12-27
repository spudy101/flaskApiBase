# Bootstrap: Terraform State Backend

## ¿Qué hace este módulo?

Este módulo crea la infraestructura necesaria para almacenar el **state** de Terraform de forma remota y segura.

### Recursos creados:

1. **S3 Bucket**: Almacena los archivos `.tfstate`
   - Versionado habilitado (permite rollback)
   - Encriptación AES256
   - Acceso público bloqueado
   - Lifecycle policy (elimina versiones antiguas después de 90 días)

2. **DynamoDB Table**: Maneja el state locking
   - Previene que múltiples personas ejecuten `terraform apply` simultáneamente
   - Billing mode: PAY_PER_REQUEST (más económico)

## ⚠️ IMPORTANTE

Este script se ejecuta **UNA SOLA VEZ** antes de cualquier otro deployment de Terraform.

## Instrucciones

### 1. Configurar variables

Edita `variables.tf` y cambia el nombre del bucket:

```hcl
variable "state_bucket_name" {
  default = "nodejs-api-terraform-state"  # 👈 Cambia esto
}
```

**Cómo obtener tu Account ID:**
para tener un nombre unico, usa tu Account ID
```bash
aws sts get-caller-identity --query Account --output text
```

### 2. Inicializar Terraform

```bash
cd terraform/bootstrap
terraform init
```

### 3. Crear el backend

```bash
terraform plan
terraform apply
```

Escribe `yes` cuando te lo pida.

### 4. Guardar los outputs

```bash
terraform output
```

**Output esperado:**
```
dynamodb_table_name = "terraform-state-lock"
state_bucket_name = "nodejs-api-terraform-state"
```

### 5. Actualizar backend.hcl en cada ambiente

Usa el nombre del bucket en los archivos:
- `environments/dev/backend.hcl`
- `environments/staging/backend.hcl`
- `environments/prod/backend.hcl`

```hcl
bucket         = "nodejs-api-terraform-state"  # 👈 Tu bucket
dynamodb_table = "terraform-state-lock"
```

## Troubleshooting

### Error: "Bucket name already exists"

El nombre del bucket S3 debe ser único **globalmente** en AWS.

**Solución:**
1. Cambia el nombre en `variables.tf`
2. Usa formato: `{project}-terraform-state-{account-id}`

### Error: "Access Denied"

Tu usuario IAM no tiene permisos para crear S3/DynamoDB.

**Solución:**
- Asigna política `AdministratorAccess` temporalmente
- O crea política custom con permisos para S3 y DynamoDB

## Limpieza (NO recomendado)

**⚠️ CUIDADO:** Esto eliminará todo el state de Terraform.

```bash
# Solo si estás 100% seguro
terraform destroy
```

**Alternativa segura:**
- Dejar el bucket y tabla creados permanentemente
- Solo cuestan centavos al mes
