# ============================================================================
# KMS Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
