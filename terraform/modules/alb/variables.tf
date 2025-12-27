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

variable "public_subnet_ids" {
  description = "IDs de las subnets públicas"
  type        = list(string)
}

variable "certificate_arn" {
  description = "ARN del certificado ACM para HTTPS"
  type        = string
  default     = ""
}

variable "container_port" {
  description = "Puerto del contenedor"
  type        = number
  default     = 3000
}

variable "health_check_path" {
  description = "Path para health check"
  type        = string
  default     = "/health"
}

variable "tags" {
  description = "Tags a aplicar"
  type        = map(string)
  default     = {}
}
