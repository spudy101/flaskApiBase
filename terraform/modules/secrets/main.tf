# ============================================================================
# Secrets Module - Secrets Manager
# ============================================================================
# Crea todos los secrets necesarios para la aplicación:
# 1. Password de DB (generado automáticamente)
# 2. JWT Secret (desde variable)
# 3. GitHub Token (desde variable - ARN existente)
# 4. Configuración de Cognito (placeholder, se llena desde root)
# ============================================================================

# ============================================================================
# Random Password para Database
# ============================================================================
resource "random_password" "db_password" {
  length  = 32
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# ============================================================================
# Secret 1: Database Credentials
# ============================================================================
resource "aws_secretsmanager_secret" "db_credentials" {
  name_prefix = "${var.project_name}-${var.environment}-db-"
  description = "Database credentials for ${var.project_name}"
  kms_key_id  = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-db-secret"
      Environment = var.environment
      Type        = "Database"
    }
  )
}

# Versión inicial con solo el password
# La información completa se actualizará desde el root module
resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    password = random_password.db_password.result
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# ============================================================================
# Secret 2: JWT Secret
# ============================================================================
resource "aws_secretsmanager_secret" "jwt_secret" {
  name_prefix = "${var.project_name}-${var.environment}-jwt-"
  description = "JWT secret for ${var.project_name}"
  kms_key_id  = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-jwt-secret"
      Environment = var.environment
      Type        = "Auth"
    }
  )
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id = aws_secretsmanager_secret.jwt_secret.id
  secret_string = jsonencode({
    jwt_secret = var.jwt_secret
  })
}

# ============================================================================
# Secret 3: GitHub Token (Referencia a secret existente)
# ============================================================================
# NOTA: Este secret debe existir previamente en AWS Secrets Manager
# Aquí solo hacemos referencia a él mediante data source
data "aws_secretsmanager_secret" "github_token" {
  arn = var.github_token_secret_arn
}

# ============================================================================
# Secret 4: Cognito Configuration (Placeholder)
# ============================================================================
# Este secret almacena IDs sensibles de Cognito que la aplicación necesita
resource "aws_secretsmanager_secret" "cognito_config" {
  name_prefix = "${var.project_name}-${var.environment}-cognito-"
  description = "Cognito configuration for ${var.project_name}"
  kms_key_id  = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-cognito-secret"
      Environment = var.environment
      Type        = "Auth"
    }
  )
}

# La versión se creará desde el root module después de crear Cognito
# para incluir todos los valores necesarios
