# ============================================================================
# ECR Module Outputs
# ============================================================================

output "repository_url" {
  description = "URL del repositorio ECR"
  value       = aws_ecr_repository.main.repository_url
}

output "repository_arn" {
  description = "ARN del repositorio ECR"
  value       = aws_ecr_repository.main.arn
}

output "repository_name" {
  description = "Nombre del repositorio ECR"
  value       = aws_ecr_repository.main.name
}

output "registry_id" {
  description = "ID del registry ECR"
  value       = aws_ecr_repository.main.registry_id
}
