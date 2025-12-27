# ============================================================================
# Lambda Module Outputs
# ============================================================================

# NOTA: Lambda functions aún no están implementadas
# Estos outputs están preparados para cuando se agreguen las funciones

output "lambda_function_arn" {
  description = "ARN de la función Lambda (placeholder - función no implementada)"
  value       = null
}

output "lambda_function_name" {
  description = "Nombre de la función Lambda (placeholder - función no implementada)"
  value       = null
}

output "lambda_role_arn" {
  description = "ARN del IAM role para Lambda"
  value       = var.create_lambda ? aws_iam_role.lambda[0].arn : null
}

output "lambda_security_group_id" {
  description = "ID del security group de Lambda"
  value       = var.create_lambda && var.enable_vpc_access ? aws_security_group.lambda[0].id : null
}

output "lambda_log_group_name" {
  description = "Nombre del CloudWatch log group"
  value       = var.create_lambda ? aws_cloudwatch_log_group.lambda[0].name : null
}