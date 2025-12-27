# ============================================================================
# KMS Module Outputs
# ============================================================================

output "secrets_key_id" {
  description = "ID de la KMS key para Secrets Manager"
  value       = aws_kms_key.secrets.id
}

output "secrets_key_arn" {
  description = "ARN de la KMS key para Secrets Manager"
  value       = aws_kms_key.secrets.arn
}

output "rds_key_id" {
  description = "ID de la KMS key para RDS"
  value       = aws_kms_key.rds.id
}

output "rds_key_arn" {
  description = "ARN de la KMS key para RDS"
  value       = aws_kms_key.rds.arn
}

output "cloudwatch_key_id" {
  description = "ID de la KMS key para CloudWatch Logs"
  value       = aws_kms_key.cloudwatch.id
}

output "cloudwatch_key_arn" {
  description = "ARN de la KMS key para CloudWatch Logs"
  value       = aws_kms_key.cloudwatch.arn
}
