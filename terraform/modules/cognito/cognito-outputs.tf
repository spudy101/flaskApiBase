# ============================================================================
# Cognito Module Outputs
# ============================================================================

# ============================================================================
# User Pool Outputs
# ============================================================================

output "user_pool_id" {
  description = "ID del Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "ARN del Cognito User Pool"
  value       = aws_cognito_user_pool.main.arn
}

output "user_pool_endpoint" {
  description = "Endpoint del Cognito User Pool"
  value       = aws_cognito_user_pool.main.endpoint
}

output "user_pool_domain" {
  description = "Dominio del Cognito User Pool"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "user_pool_domain_cloudfront" {
  description = "CloudFront distribution del User Pool Domain"
  value       = aws_cognito_user_pool_domain.main.cloudfront_distribution
}

# ============================================================================
# Web App Client Outputs
# ============================================================================

output "web_client_id" {
  description = "ID del App Client Web"
  value       = aws_cognito_user_pool_client.web.id
}

output "web_client_name" {
  description = "Nombre del App Client Web"
  value       = aws_cognito_user_pool_client.web.name
}

# ============================================================================
# Mobile App Client Outputs (si está habilitado)
# ============================================================================

output "mobile_client_id" {
  description = "ID del App Client Mobile (si está habilitado)"
  value       = var.create_mobile_client ? aws_cognito_user_pool_client.mobile[0].id : null
}

output "mobile_client_secret" {
  description = "Secret del App Client Mobile (SENSIBLE)"
  value       = var.create_mobile_client ? aws_cognito_user_pool_client.mobile[0].client_secret : null
  sensitive   = true
}

# ============================================================================
# Identity Pool Outputs (si está habilitado)
# ============================================================================

output "identity_pool_id" {
  description = "ID del Cognito Identity Pool (si está habilitado)"
  value       = var.create_identity_pool ? aws_cognito_identity_pool.main[0].id : null
}

output "identity_pool_arn" {
  description = "ARN del Cognito Identity Pool (si está habilitado)"
  value       = var.create_identity_pool ? aws_cognito_identity_pool.main[0].arn : null
}

output "authenticated_role_arn" {
  description = "ARN del IAM Role para usuarios autenticados (si está habilitado)"
  value       = var.create_identity_pool ? aws_iam_role.authenticated[0].arn : null
}

# ============================================================================
# Hosted UI URL
# ============================================================================

output "hosted_ui_url" {
  description = "URL del Hosted UI de Cognito"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
}

# ============================================================================
# OAuth Endpoints
# ============================================================================

output "oauth_authorize_endpoint" {
  description = "Endpoint de autorización OAuth"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${data.aws_region.current.name}.amazoncognito.com/oauth2/authorize"
}

output "oauth_token_endpoint" {
  description = "Endpoint de token OAuth"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${data.aws_region.current.name}.amazoncognito.com/oauth2/token"
}

output "oauth_userinfo_endpoint" {
  description = "Endpoint de userInfo OAuth"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${data.aws_region.current.name}.amazoncognito.com/oauth2/userInfo"
}

# ============================================================================
# JWKS URL (para validar tokens)
# ============================================================================

output "jwks_url" {
  description = "URL de JSON Web Key Set para validar tokens JWT"
  value       = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.main.id}/.well-known/jwks.json"
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_region" "current" {}
