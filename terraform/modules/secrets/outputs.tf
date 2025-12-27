# ============================================================================
# Secrets Module Outputs
# ============================================================================

# ============================================================================
# Database Secret Outputs
# ============================================================================

output "db_password" {
  description = "Database password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "secret_id" {
  description = "Secret Manager secret ID para DB"
  value       = aws_secretsmanager_secret.db_credentials.id
}

output "secret_arn" {
  description = "Secret Manager secret ARN para DB"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "secret_name" {
  description = "Secret Manager secret name para DB"
  value       = aws_secretsmanager_secret.db_credentials.name
}

# ============================================================================
# JWT Secret Outputs
# ============================================================================

output "jwt_secret_id" {
  description = "Secret Manager secret ID para JWT"
  value       = aws_secretsmanager_secret.jwt_secret.id
}

output "jwt_secret_arn" {
  description = "Secret Manager secret ARN para JWT"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "jwt_secret_name" {
  description = "Secret Manager secret name para JWT"
  value       = aws_secretsmanager_secret.jwt_secret.name
}

# ============================================================================
# GitHub Token Secret Outputs
# ============================================================================

output "github_token_secret_arn" {
  description = "ARN del secret de GitHub token (referencia)"
  value       = data.aws_secretsmanager_secret.github_token.arn
}

output "github_token_secret_id" {
  description = "ID del secret de GitHub token (referencia)"
  value       = data.aws_secretsmanager_secret.github_token.id
}

# ============================================================================
# Cognito Secret Outputs
# ============================================================================

output "cognito_secret_id" {
  description = "Secret Manager secret ID para Cognito"
  value       = aws_secretsmanager_secret.cognito_config.id
}

output "cognito_secret_arn" {
  description = "Secret Manager secret ARN para Cognito"
  value       = aws_secretsmanager_secret.cognito_config.arn
}

output "cognito_secret_name" {
  description = "Secret Manager secret name para Cognito"
  value       = aws_secretsmanager_secret.cognito_config.name
}
