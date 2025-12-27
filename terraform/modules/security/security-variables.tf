# ============================================================================
# Security Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "enable_alerts" {
  description = "Habilitar alertas por email para findings críticos"
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Email para recibir alertas de seguridad"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
