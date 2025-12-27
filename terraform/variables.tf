# General
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "nodejs-api"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# VPC
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Database
variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nodejsdb"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "dbadmin"
}

variable "db_port" {
  description = "Database port"
  type        = number
  default     = 5432
}

variable "db_schema" {
  description = "Database schema"
  type        = string
  default     = "public"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_multi_az" {
  description = "Enable Multi-AZ"
  type        = bool
  default     = false
}

variable "db_backup_retention" {
  description = "Backup retention (days)"
  type        = number
  default     = 7
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot"
  type        = bool
  default     = false
}

# Secrets
variable "jwt_secret" {
  description = "JWT secret"
  type        = string
  sensitive   = true
}

variable "github_token_secret_arn" {
  description = "GitHub token secret ARN"
  type        = string
}

# Cognito
variable "cognito_web_callback_urls" {
  description = "Web callback URLs"
  type        = list(string)
  default     = ["http://localhost:3000/callback"]
}

variable "cognito_web_logout_urls" {
  description = "Web logout URLs"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "cognito_enable_mobile_client" {
  description = "Enable mobile client"
  type        = bool
  default     = false
}

variable "cognito_mobile_callback_urls" {
  description = "Mobile callback URLs"
  type        = list(string)
  default     = []
}

variable "cognito_mobile_logout_urls" {
  description = "Mobile logout URLs"
  type        = list(string)
  default     = []
}

variable "cognito_enable_identity_pool" {
  description = "Enable identity pool"
  type        = bool
  default     = false
}

# ECS
variable "ecs_cpu" {
  description = "ECS task CPU (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "ecs_memory" {
  description = "ECS task memory (MB)"
  type        = number
  default     = 1024
}

variable "ecs_desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 2
}

variable "ecs_min_capacity" {
  description = "Min tasks for auto scaling"
  type        = number
  default     = 1
}

variable "ecs_max_capacity" {
  description = "Max tasks for auto scaling"
  type        = number
  default     = 10
}

variable "ecs_image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

# Container
variable "container_port" {
  description = "Container port"
  type        = number
  default     = 3000
}

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/health"
}

# ECR
variable "ecr_image_retention_count" {
  description = "Number of images to retain in ECR"
  type        = number
  default     = 10
}

# ALB
variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}
