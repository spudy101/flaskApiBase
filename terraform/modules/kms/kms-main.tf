# ============================================================================
# KMS Module - Encryption Keys
# ============================================================================
# Crea KMS keys para cifrar:
# - Secrets Manager secrets
# - RDS snapshots y storage
# - CloudWatch Logs
# - S3 buckets (si se necesita)
# ============================================================================

# ============================================================================
# KMS Key para Secrets Manager
# ============================================================================

resource "aws_kms_key" "secrets" {
  description             = "${var.project_name}-${var.environment} - Secrets Manager encryption key"
  deletion_window_in_days = var.environment == "prod" ? 30 : 7
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name    = "${var.project_name}-${var.environment}-secrets-key"
      Purpose = "secrets-manager"
    }
  )
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${var.project_name}-${var.environment}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# ============================================================================
# KMS Key para RDS
# ============================================================================

resource "aws_kms_key" "rds" {
  description             = "${var.project_name}-${var.environment} - RDS encryption key"
  deletion_window_in_days = var.environment == "prod" ? 30 : 7
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name    = "${var.project_name}-${var.environment}-rds-key"
      Purpose = "rds"
    }
  )
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.project_name}-${var.environment}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# ============================================================================
# KMS Key para CloudWatch Logs
# ============================================================================

resource "aws_kms_key" "cloudwatch" {
  description             = "${var.project_name}-${var.environment} - CloudWatch Logs encryption key"
  deletion_window_in_days = var.environment == "prod" ? 30 : 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name    = "${var.project_name}-${var.environment}-cloudwatch-key"
      Purpose = "cloudwatch-logs"
    }
  )
}

resource "aws_kms_alias" "cloudwatch" {
  name          = "alias/${var.project_name}-${var.environment}-cloudwatch"
  target_key_id = aws_kms_key.cloudwatch.key_id
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
