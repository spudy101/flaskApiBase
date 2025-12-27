# ============================================================================
# Cognito Module - User Authentication
# ============================================================================
# Crea:
# - User Pool (almacén de usuarios)
# - User Pool Domain (para Hosted UI)
# - App Clients (web, mobile, etc)
# - Identity Pool (opcional, para acceso AWS)
# ============================================================================

# ============================================================================
# Cognito User Pool
# ============================================================================
resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-${var.environment}-user-pool"

  # ============================================================================
  # Atributos de Usuario
  # ============================================================================
  # Atributos que NO se pueden cambiar después de crear el pool
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = false

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  schema {
    name                = "name"
    attribute_data_type = "String"
    required            = false
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  schema {
    name                = "phone_number"
    attribute_data_type = "String"
    required            = false
    mutable             = true

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }

  # Atributos personalizados (opcional)
  schema {
    name                = "company"
    attribute_data_type = "String"
    mutable             = true

    string_attribute_constraints {
      min_length = 0
      max_length = 256
    }
  }

  # ============================================================================
  # Alias (formas de login)
  # ============================================================================
  username_attributes      = ["email"]  # Login con email
  auto_verified_attributes = ["email"]  # Verificar email automáticamente

  # ============================================================================
  # Políticas de Contraseña
  # ============================================================================
  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 7
  }

  # ============================================================================
  # Configuración de MFA (Multi-Factor Authentication)
  # ============================================================================
  mfa_configuration = var.enable_mfa ? "OPTIONAL" : "OFF"

  dynamic "software_token_mfa_configuration" {
    for_each = var.enable_mfa ? [1] : []
    content {
      enabled = true
    }
  }

  # ============================================================================
  # Recuperación de Cuenta
  # ============================================================================
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }

    recovery_mechanism {
      name     = "verified_phone_number"
      priority = 2
    }
  }

  # ============================================================================
  # Configuración de Email
  # ============================================================================
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"  # Usar email de Cognito (gratis hasta 50/día)
    # Para producción, considera usar SES:
    # email_sending_account = "DEVELOPER"
    # source_arn = var.ses_email_arn
  }

  # ============================================================================
  # Mensajes de Verificación
  # ============================================================================
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "${var.project_name} - Verifica tu email"
    email_message        = "Tu código de verificación es {####}"
  }

  # ============================================================================
  # Prevención de Bots
  # ============================================================================
  user_pool_add_ons {
    advanced_security_mode = var.environment == "prod" ? "ENFORCED" : "AUDIT"
  }

  # ============================================================================
  # Protección contra Ataques
  # ============================================================================
  lambda_config {
    # Pre-autenticación (validaciones antes de login)
    # pre_authentication = var.pre_auth_lambda_arn

    # Post-autenticación (acciones después de login)
    # post_authentication = var.post_auth_lambda_arn

    # Pre-registro (validaciones antes de crear cuenta)
    # pre_sign_up = var.pre_signup_lambda_arn

    # Post-confirmación (acciones después de confirmar email)
    # post_confirmation = var.post_confirmation_lambda_arn
  }

  # ============================================================================
  # Políticas de Dispositivos
  # ============================================================================
  device_configuration {
    challenge_required_on_new_device      = false
    device_only_remembered_on_user_prompt = true
  }

  # ============================================================================
  # Prevención de Eliminación Accidental
  # ============================================================================
  deletion_protection = var.environment == "prod" ? "ACTIVE" : "INACTIVE"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-user-pool"
    }
  )
}

# ============================================================================
# Cognito User Pool Domain (para Hosted UI)
# ============================================================================
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${var.environment}-${random_string.domain_suffix.result}"
  user_pool_id = aws_cognito_user_pool.main.id
}

resource "random_string" "domain_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ============================================================================
# App Client - Web Application
# ============================================================================
resource "aws_cognito_user_pool_client" "web" {
  name         = "${var.project_name}-${var.environment}-web-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # OAuth2 configuration
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["phone", "email", "openid", "profile"]

  callback_urls = var.web_callback_urls
  logout_urls   = var.web_logout_urls

  # Security
  generate_secret                      = false  # Web no necesita secret (SPA)
  prevent_user_existence_errors        = "ENABLED"
  enable_token_revocation             = true
  enable_propagate_additional_user_context_data = false

  # Token validity
  access_token_validity  = 60   # minutos
  id_token_validity      = 60   # minutos
  refresh_token_validity = 30   # días

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Explicit auth flows
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"  # Solo para desarrollo/testing
  ]

  # Read/Write attributes
  read_attributes  = ["email", "name", "phone_number", "email_verified"]
  write_attributes = ["email", "name", "phone_number"]
}

# ============================================================================
# App Client - Mobile Application (con secret)
# ============================================================================
resource "aws_cognito_user_pool_client" "mobile" {
  count = var.create_mobile_client ? 1 : 0

  name         = "${var.project_name}-${var.environment}-mobile-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # OAuth2 configuration
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["phone", "email", "openid", "profile"]

  callback_urls = var.mobile_callback_urls
  logout_urls   = var.mobile_logout_urls

  # Security
  generate_secret                      = true  # Mobile necesita secret
  prevent_user_existence_errors        = "ENABLED"
  enable_token_revocation             = true
  enable_propagate_additional_user_context_data = false

  # Token validity
  access_token_validity  = 60   # minutos
  id_token_validity      = 60   # minutos
  refresh_token_validity = 30   # días

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Explicit auth flows
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  # Read/Write attributes
  read_attributes  = ["email", "name", "phone_number", "email_verified"]
  write_attributes = ["email", "name", "phone_number"]
}

# ============================================================================
# Identity Pool (Opcional - para acceso a AWS)
# ============================================================================
resource "aws_cognito_identity_pool" "main" {
  count = var.create_identity_pool ? 1 : 0

  identity_pool_name               = "${var.project_name}-${var.environment}-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.web.id
    provider_name           = aws_cognito_user_pool.main.endpoint
    server_side_token_check = false
  }

  # Providers externos (Google, Facebook, etc)
  # supported_login_providers = {
  #   "accounts.google.com" = var.google_client_id
  # }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-identity-pool"
    }
  )
}

# ============================================================================
# IAM Roles para Identity Pool (si está habilitado)
# ============================================================================
resource "aws_iam_role" "authenticated" {
  count = var.create_identity_pool ? 1 : 0

  name = "${var.project_name}-${var.environment}-cognito-authenticated"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.main[0].id
          }
          "ForAnyValue:StringLike" = {
            "cognito-identity.amazonaws.com:amr" = "authenticated"
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "authenticated" {
  count = var.create_identity_pool ? 1 : 0

  name = "${var.project_name}-${var.environment}-authenticated-policy"
  role = aws_iam_role.authenticated[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-user-uploads/*"
        ]
      }
    ]
  })
}

# Attach role to identity pool
resource "aws_cognito_identity_pool_roles_attachment" "main" {
  count = var.create_identity_pool ? 1 : 0

  identity_pool_id = aws_cognito_identity_pool.main[0].id

  roles = {
    authenticated = aws_iam_role.authenticated[0].arn
  }
}
