# ============================================================================
# Database Module Variables
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

variable "database_subnet_ids" {
  description = "IDs de las subnets privadas para RDS"
  type        = list(string)
}

variable "allowed_security_groups" {
  description = "Security groups que pueden acceder a RDS"
  type        = list(string)
}

variable "instance_class" {
  description = "Clase de instancia RDS"
  type        = string
}

variable "allocated_storage" {
  description = "Almacenamiento en GB"
  type        = number
}

variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
}

variable "db_schema" {
  description = "Schema de PostgreSQL (se crea con init-schema.sql)"
  type        = string
  default     = "app_schema"
}

variable "db_username" {
  description = "Usuario master de la base de datos"
  type        = string
}

variable "db_password" {
  description = "Password de la base de datos"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "Puerto de la base de datos"
  type        = number
  default     = 5432
}

variable "multi_az" {
  description = "Habilitar Multi-AZ"
  type        = bool
  default     = false
}

variable "backup_retention" {
  description = "Días de retención de backups"
  type        = number
  default     = 7
}

variable "skip_final_snapshot" {
  description = "Omitir snapshot final al destruir (solo dev/staging)"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "ARN de la KMS key para cifrado"
  type        = string
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
