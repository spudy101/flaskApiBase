# ============================================================================
# Cognito Module Variables
# ============================================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

# ============================================================================
# User Pool Configuration
# ============================================================================

variable "enable_mfa" {
  description = "Habilitar MFA (Multi-Factor Authentication)"
  type        = bool
  default     = false
}

# ============================================================================
# Web App Client Configuration
# ============================================================================

variable "web_callback_urls" {
  description = "URLs de callback para el cliente web"
  type        = list(string)
  default     = ["http://localhost:3000/callback"]
}

variable "web_logout_urls" {
  description = "URLs de logout para el cliente web"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

# ============================================================================
# Mobile App Client Configuration
# ============================================================================

variable "create_mobile_client" {
  description = "Crear app client para aplicación móvil"
  type        = bool
  default     = false
}

variable "mobile_callback_urls" {
  description = "URLs de callback para el cliente móvil"
  type        = list(string)
  default     = ["myapp://callback"]
}

variable "mobile_logout_urls" {
  description = "URLs de logout para el cliente móvil"
  type        = list(string)
  default     = ["myapp://logout"]
}

# ============================================================================
# Identity Pool Configuration
# ============================================================================

variable "create_identity_pool" {
  description = "Crear Identity Pool para acceso a AWS"
  type        = bool
  default     = false
}

# ============================================================================
# Email Configuration
# ============================================================================

variable "ses_email_arn" {
  description = "ARN de email verificado en SES (opcional, para producción)"
  type        = string
  default     = ""
}

# ============================================================================
# Lambda Triggers (Opcional)
# ============================================================================

variable "pre_auth_lambda_arn" {
  description = "ARN de Lambda para pre-autenticación"
  type        = string
  default     = ""
}

variable "post_auth_lambda_arn" {
  description = "ARN de Lambda para post-autenticación"
  type        = string
  default     = ""
}

variable "pre_signup_lambda_arn" {
  description = "ARN de Lambda para pre-registro"
  type        = string
  default     = ""
}

variable "post_confirmation_lambda_arn" {
  description = "ARN de Lambda para post-confirmación"
  type        = string
  default     = ""
}

# ============================================================================
# Tags
# ============================================================================

variable "tags" {
  description = "Tags a aplicar a todos los recursos"
  type        = map(string)
  default     = {}
}
