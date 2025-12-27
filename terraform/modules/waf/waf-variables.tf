# ============================================================================
# WAF Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "rate_limit" {
  description = "Límite de requests por IP (por 5 minutos)"
  type        = number
  default     = 1000
}

variable "blocked_ip_addresses" {
  description = "Lista de IPs a bloquear (formato CIDR)"
  type        = list(string)
  default     = []
}

variable "blocked_countries" {
  description = "Lista de códigos de países a bloquear (ISO 3166-1 alpha-2)"
  type        = list(string)
  default     = []
  
  # Ejemplos: ["CN", "RU", "KP"]
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
