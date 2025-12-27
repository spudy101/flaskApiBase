# ============================================================================
# Lambda Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "create_lambda" {
  description = "Crear recursos Lambda (false por ahora, true en siguiente fase)"
  type        = bool
  default     = false
}

variable "enable_vpc_access" {
  description = "Habilitar acceso a VPC (para conectar a RDS)"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "ID de la VPC"
  type        = string
  default     = ""
}

variable "private_subnet_ids" {
  description = "IDs de las subnets privadas para Lambda"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
