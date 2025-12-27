# ============================================================================
# Database Module Outputs
# ============================================================================

output "db_instance_id" {
  description = "ID de la instancia RDS"
  value       = aws_db_instance.main.id
}

output "db_endpoint" {
  description = "Endpoint de la base de datos (host:port)"
  value       = aws_db_instance.main.endpoint
}

output "db_address" {
  description = "Dirección del host de la base de datos (sin puerto)"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "Puerto de la base de datos"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Nombre de la base de datos"
  value       = aws_db_instance.main.db_name
}

output "db_arn" {
  description = "ARN de la instancia RDS"
  value       = aws_db_instance.main.arn
}

output "security_group_id" {
  description = "ID del security group de RDS"
  value       = aws_security_group.rds.id
}
