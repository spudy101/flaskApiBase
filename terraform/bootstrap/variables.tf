# ============================================================================
# Variables para Bootstrap de Terraform (Backend remoto en AWS)
# ============================================================================

variable "region" {
  description = "Región de AWS donde se crearán los recursos de bootstrap, incluyendo el bucket S3 y la tabla DynamoDB utilizados por el backend remoto de Terraform."
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Nombre del bucket de Amazon S3 que almacenará el archivo de estado remoto de Terraform (terraform.tfstate). Este bucket debe ser único a nivel global y se utiliza para mantener el estado de la infraestructura de forma segura y centralizada."
  type        = string
  default     = "nodejs-api-terraform-state"

  validation {
    condition     = length(var.state_bucket_name) >= 3 && length(var.state_bucket_name) <= 63
    error_message = "El nombre del bucket debe tener entre 3 y 63 caracteres."
  }
}

variable "dynamodb_table_name" {
  description = "Nombre de la tabla de Amazon DynamoDB utilizada para el bloqueo del estado de Terraform (state locking), evitando ejecuciones concurrentes que puedan causar inconsistencias en la infraestructura."
  type        = string
  default     = "terraform-state-lock"
}
