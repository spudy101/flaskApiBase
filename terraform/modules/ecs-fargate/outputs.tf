# ============================================================================
# ECS Fargate Module Outputs
# ============================================================================

output "cluster_id" {
  description = "ID del cluster ECS"
  value       = aws_ecs_cluster.main.id
}

output "cluster_arn" {
  description = "ARN del cluster ECS"
  value       = aws_ecs_cluster.main.arn
}

output "cluster_name" {
  description = "Nombre del cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "service_id" {
  description = "ID del servicio ECS"
  value       = aws_ecs_service.main.id
}

output "service_name" {
  description = "Nombre del servicio ECS"
  value       = aws_ecs_service.main.name
}

output "task_definition_arn" {
  description = "ARN de la task definition"
  value       = aws_ecs_task_definition.main.arn
}

output "task_execution_role_arn" {
  description = "ARN del execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "task_role_arn" {
  description = "ARN del task role"
  value       = aws_iam_role.ecs_task.arn
}

output "security_group_id" {
  description = "ID del security group de las tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "log_group_name" {
  description = "Nombre del CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
}
