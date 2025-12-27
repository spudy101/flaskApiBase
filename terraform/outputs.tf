# Networking
output "vpc_id" {
  value = module.networking.vpc_id
}

output "alb_dns_name" {
  description = "DNS del ALB para acceder a la aplicación"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  description = "URL completa del ALB"
  value       = "http://${module.alb.alb_dns_name}"
}

# ECR
output "ecr_repository_url" {
  description = "URL del repositorio ECR (para docker push)"
  value       = module.ecr.repository_url
}

# ECS
output "ecs_cluster_name" {
  description = "Nombre del cluster ECS"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Nombre del servicio ECS"
  value       = module.ecs.service_name
}

# Database
output "database_endpoint" {
  value = module.database.db_endpoint
}

output "database_name" {
  value = var.db_name
}

# Secrets
output "db_credentials_secret_arn" {
  value = module.secrets.secret_arn
}

# Comandos útiles
output "useful_commands" {
  value = <<-EOT
    
    ╔════════════════════════════════════════════════════╗
    ║         COMANDOS ÚTILES - ${upper(var.environment)}                  ║
    ╚════════════════════════════════════════════════════╝
    
    🚀 ACCEDER A LA APLICACIÓN
    http://${module.alb.alb_dns_name}
    
    📦 SUBIR NUEVA IMAGEN A ECR
    aws ecr get-login-password --region ${var.aws_region} | \
      docker login --username AWS --password-stdin ${module.ecr.repository_url}
    
    docker build -t ${var.project_name} .
    docker tag ${var.project_name}:latest ${module.ecr.repository_url}:latest
    docker push ${module.ecr.repository_url}:latest
    
    🔄 FORZAR NUEVO DEPLOYMENT
    aws ecs update-service \
      --cluster ${module.ecs.cluster_name} \
      --service ${module.ecs.service_name} \
      --force-new-deployment
    
    📊 VER LOGS
    aws logs tail /ecs/${var.project_name}-${var.environment} --follow
    
    🗄️  CONECTAR A DATABASE
    psql -h ${module.database.db_address} -U ${var.db_username} -d ${var.db_name}
    
    ════════════════════════════════════════════════════
  EOT
}
