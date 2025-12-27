# ============================================================================
# ECS Fargate Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID de la VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "IDs de las subnets privadas para ECS tasks"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ID del security group del ALB"
  type        = string
}

variable "target_group_arn" {
  description = "ARN del target group del ALB"
  type        = string
}

variable "alb_listener_arn" {
  description = "ARN del listener del ALB (para depends_on)"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL del repositorio ECR"
  type        = string
}

variable "image_tag" {
  description = "Tag de la imagen Docker a desplegar"
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Puerto del contenedor"
  type        = number
  default     = 3000
}

variable "cpu" {
  description = "CPU para la tarea (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Memoria para la tarea en MB"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Número deseado de tareas"
  type        = number
  default     = 2
}

variable "min_capacity" {
  description = "Capacidad mínima de auto scaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Capacidad máxima de auto scaling"
  type        = number
  default     = 10
}

variable "environment_variables" {
  description = "Variables de entorno para el contenedor"
  type        = map(string)
  default     = {}
}

variable "environment_secrets" {
  description = "Secrets desde Secrets Manager (map de nombre -> ARN)"
  type        = map(string)
  default     = {}
}

variable "secrets_arns" {
  description = "Lista de ARNs de secrets para IAM policy"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags a aplicar"
  type        = map(string)
  default     = {}
}
