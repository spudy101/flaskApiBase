# ============================================================================
# ECR Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "image_retention_count" {
  description = "Número de imágenes a retener"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Tags a aplicar"
  type        = map(string)
  default     = {}
}
