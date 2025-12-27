# ============================================================================
# Root Main Configuration - Multi-Environment with ECS Fargate
# ============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  # ALB siempre se crea (requerido por ECS Fargate)
  create_alb      = true
  create_waf      = var.environment == "prod"
  create_security = var.environment == "prod"
  enable_vpc_endpoints = var.environment != "dev"
  nat_gateway_count = var.environment == "prod" ? 2 : 1
}

# 1. KMS
module "kms" {
  source = "./modules/kms"
  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}

# 2. Networking
module "networking" {
  source = "./modules/networking"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  nat_gateway_count    = local.nat_gateway_count
  enable_vpc_endpoints = local.enable_vpc_endpoints
  enable_rds_endpoint  = false
  tags = local.common_tags
}

# 3. Secrets
module "secrets" {
  source = "./modules/secrets"
  project_name             = var.project_name
  environment              = var.environment
  kms_key_id               = module.kms.secrets_key_id
  jwt_secret               = var.jwt_secret
  github_token_secret_arn  = var.github_token_secret_arn
  tags = local.common_tags
}

# 4. Cognito
module "cognito" {
  source = "./modules/cognito"
  project_name = var.project_name
  environment  = var.environment
  enable_mfa = var.environment == "prod"
  web_callback_urls    = var.cognito_web_callback_urls
  web_logout_urls      = var.cognito_web_logout_urls
  create_mobile_client = var.cognito_enable_mobile_client
  mobile_callback_urls = var.cognito_mobile_callback_urls
  mobile_logout_urls   = var.cognito_mobile_logout_urls
  create_identity_pool = var.cognito_enable_identity_pool
  tags = local.common_tags
}

# 5. Update Cognito Secret
resource "aws_secretsmanager_secret_version" "cognito_config" {
  secret_id = module.secrets.cognito_secret_id
  secret_string = jsonencode({
    user_pool_id             = module.cognito.user_pool_id
    user_pool_arn            = module.cognito.user_pool_arn
    web_client_id            = module.cognito.web_client_id
    mobile_client_id         = module.cognito.mobile_client_id
    mobile_client_secret     = module.cognito.mobile_client_secret
    identity_pool_id         = module.cognito.identity_pool_id
    region                   = var.aws_region
    hosted_ui_url            = module.cognito.hosted_ui_url
    oauth_authorize_endpoint = module.cognito.oauth_authorize_endpoint
    oauth_token_endpoint     = module.cognito.oauth_token_endpoint
    oauth_userinfo_endpoint  = module.cognito.oauth_userinfo_endpoint
    jwks_url                 = module.cognito.jwks_url
  })
  depends_on = [module.cognito, module.secrets]
}

# 6. Database
module "database" {
  source = "./modules/database"
  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.networking.vpc_id
  database_subnet_ids     = module.networking.database_subnet_ids
  allowed_security_groups = []
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = module.secrets.db_password
  db_port             = var.db_port
  db_schema           = var.db_schema
  instance_class      = var.db_instance_class
  allocated_storage   = var.db_allocated_storage
  multi_az            = var.db_multi_az
  backup_retention    = var.db_backup_retention
  skip_final_snapshot = var.skip_final_snapshot
  kms_key_arn         = module.kms.secrets_key_arn
  tags = local.common_tags
}

# 7. Update DB Secret
resource "aws_secretsmanager_secret_version" "db_credentials_complete" {
  secret_id = module.secrets.secret_id
  secret_string = jsonencode({
    username = var.db_username
    password = module.secrets.db_password
    host     = module.database.db_address
    port     = module.database.db_port
    dbname   = module.database.db_name
    engine   = "postgres"
    endpoint = module.database.db_endpoint
    schema   = var.db_schema
  })
  depends_on = [module.database, module.secrets]
}

# 8. ECR - Container Registry
module "ecr" {
  source = "./modules/ecr"
  project_name = var.project_name
  environment  = var.environment
  image_retention_count = var.ecr_image_retention_count
  tags = local.common_tags
}

# 9. ALB - Application Load Balancer
module "alb" {
  source = "./modules/alb"
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.networking.vpc_id
  public_subnet_ids = module.networking.public_subnet_ids
  certificate_arn   = var.certificate_arn
  container_port    = var.container_port
  health_check_path = var.health_check_path
  tags = local.common_tags
}

# 10. ECS Fargate
module "ecs" {
  source = "./modules/ecs-fargate"
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  alb_security_group_id = module.alb.alb_security_group_id
  target_group_arn      = module.alb.target_group_arn
  alb_listener_arn      = module.alb.http_listener_arn
  ecr_repository_url    = module.ecr.repository_url
  image_tag             = var.ecs_image_tag
  container_port        = var.container_port
  cpu                   = var.ecs_cpu
  memory                = var.ecs_memory
  desired_count         = var.ecs_desired_count
  min_capacity          = var.ecs_min_capacity
  max_capacity          = var.ecs_max_capacity
  
  environment_variables = {
    NODE_ENV             = var.environment
    DB_HOST              = module.database.db_address
    DB_NAME              = var.db_name
    DB_PORT              = tostring(var.db_port)
    COGNITO_USER_POOL_ID = module.cognito.user_pool_id
    COGNITO_CLIENT_ID    = module.cognito.web_client_id
    AWS_REGION           = var.aws_region
  }
  
  environment_secrets = {
    DB_SECRET_ARN      = module.secrets.secret_arn
    JWT_SECRET_ARN     = module.secrets.jwt_secret_arn
    COGNITO_SECRET_ARN = module.secrets.cognito_secret_arn
  }
  
  secrets_arns = [
    module.secrets.secret_arn,
    module.secrets.jwt_secret_arn,
    module.secrets.cognito_secret_arn
  ]
  
  tags = local.common_tags
  depends_on = [
    module.database,
    module.cognito,
    aws_secretsmanager_secret_version.db_credentials_complete,
    aws_secretsmanager_secret_version.cognito_config
  ]
}

# 11. Lambda
module "lambda" {
  source = "./modules/lambda"
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  tags = local.common_tags
}

# 12. WAF
module "waf" {
  count = local.create_waf ? 1 : 0
  source = "./modules/waf"
  project_name = var.project_name
  environment  = var.environment
  tags = local.common_tags
}

resource "aws_wafv2_web_acl_association" "alb" {
  count = local.create_waf ? 1 : 0
  resource_arn = module.alb.alb_arn
  web_acl_arn  = module.waf[0].web_acl_arn
  depends_on = [module.alb, module.waf]
}

# 13. Security
module "security" {
  count = local.create_security ? 1 : 0
  source = "./modules/security"
  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}
