# ============================================================================
# Networking Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block para la VPC"
  type        = string
}

variable "availability_zones" {
  description = "Lista de Availability Zones"
  type        = list(string)
}

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}

# ============================================================================
# VPC Endpoints Configuration
# ============================================================================

variable "enable_vpc_endpoints" {
  description = "Habilitar VPC endpoints para reducir costos de NAT"
  type        = bool
  default     = false
}

variable "enable_rds_endpoint" {
  description = "Habilitar RDS endpoint (raramente necesario)"
  type        = bool
  default     = false
}

variable "nat_gateway_count" {
  description = "Número de NAT Gateways (1=costo reducido, 2=alta disponibilidad)"
  type        = number
  default     = 2
  
  validation {
    condition     = var.nat_gateway_count >= 1 && var.nat_gateway_count <= 3
    error_message = "nat_gateway_count debe estar entre 1 y 3"
  }
}
