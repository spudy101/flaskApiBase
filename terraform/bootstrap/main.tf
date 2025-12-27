# ============================================================================
# BOOTSTRAP: Terraform State Backend
# ============================================================================
# Este archivo crea la infraestructura necesaria para almacenar el state
# de Terraform de forma remota y segura.
#
# Recursos creados:
# - S3 Bucket: Almacena los archivos .tfstate
# - DynamoDB Table: Maneja el locking para evitar conflictos en equipo
#
# IMPORTANTE: Este script se ejecuta UNA SOLA VEZ antes de cualquier
# otro deployment de Terraform.
# ============================================================================

terraform {
  required_version = ">= 1.9.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Project     = "nodejs-api"
      ManagedBy   = "terraform"
      Component   = "state-backend"
      Environment = "global"
    }
  }
}

# ============================================================================
# S3 Bucket para Terraform State
# ============================================================================

resource "aws_s3_bucket" "terraform_state" {
  bucket = var.state_bucket_name

  # Prevenir eliminación accidental del bucket
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Bucket"
    Description = "Stores Terraform state files for all environments"
  }
}

# Habilitar versionado (importante para rollback)
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Habilitar encriptación en reposo
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloquear acceso público (seguridad)
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Política de ciclo de vida (opcional: borrar versiones antiguas después de 90 días)
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# ============================================================================
# DynamoDB Table para State Locking
# ============================================================================

resource "aws_dynamodb_table" "terraform_locks" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"  # Más económico que PROVISIONED
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  # Prevenir eliminación accidental
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Lock Table"
    Description = "Handles state locking for Terraform operations"
  }
}

# ============================================================================
# Outputs
# ============================================================================

output "state_bucket_name" {
  description = "Nombre del bucket S3 para el state"
  value       = aws_s3_bucket.terraform_state.id
}

output "state_bucket_arn" {
  description = "ARN del bucket S3"
  value       = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB para locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "dynamodb_table_arn" {
  description = "ARN de la tabla DynamoDB"
  value       = aws_dynamodb_table.terraform_locks.arn
}
