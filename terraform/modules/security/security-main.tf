# ============================================================================
# Security Module - GuardDuty + Inspector
# ============================================================================
# GuardDuty: Detección de amenazas en tiempo real
# Inspector: Escaneo de vulnerabilidades
# ============================================================================

# ============================================================================
# Amazon GuardDuty
# ============================================================================

resource "aws_guardduty_detector" "main" {
  enable = true

  # Habilitar análisis de logs
  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false  # No tenemos EKS
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  # Frecuencia de publicación de findings
  finding_publishing_frequency = "FIFTEEN_MINUTES"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-guardduty"
    }
  )
}

# ============================================================================
# CloudWatch Log Group para GuardDuty Findings
# ============================================================================

resource "aws_cloudwatch_log_group" "guardduty" {
  name              = "/aws/guardduty/${var.project_name}-${var.environment}"
  retention_in_days = var.environment == "prod" ? 90 : 30

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-guardduty-logs"
    }
  )
}

# ============================================================================
# SNS Topic para alertas de GuardDuty (opcional)
# ============================================================================

resource "aws_sns_topic" "guardduty_alerts" {
  count = var.enable_alerts ? 1 : 0
  name  = "${var.project_name}-${var.environment}-guardduty-alerts"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-guardduty-alerts"
    }
  )
}

resource "aws_sns_topic_subscription" "guardduty_email" {
  count     = var.enable_alerts && var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.guardduty_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ============================================================================
# EventBridge Rule para enviar findings a SNS
# ============================================================================

resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  count       = var.enable_alerts ? 1 : 0
  name        = "${var.project_name}-${var.environment}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [7, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9]  # HIGH and CRITICAL only
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "guardduty_sns" {
  count     = var.enable_alerts ? 1 : 0
  rule      = aws_cloudwatch_event_rule.guardduty_findings[0].name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.guardduty_alerts[0].arn
}

resource "aws_sns_topic_policy" "guardduty_alerts" {
  count  = var.enable_alerts ? 1 : 0
  arn    = aws_sns_topic.guardduty_alerts[0].arn
  policy = data.aws_iam_policy_document.guardduty_sns_policy[0].json
}

data "aws_iam_policy_document" "guardduty_sns_policy" {
  count = var.enable_alerts ? 1 : 0

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    actions = ["SNS:Publish"]

    resources = [aws_sns_topic.guardduty_alerts[0].arn]
  }
}

# ============================================================================
# Amazon Inspector v2
# ============================================================================

resource "aws_inspector2_enabler" "main" {
  account_ids = [data.aws_caller_identity.current.account_id]
  
  resource_types = [
    "ECR",      # Escaneo de imágenes Docker (si usas ECR)
    "EC2",      # Escaneo de instancias EC2 (si tienes)
    "LAMBDA",   # Escaneo de funciones Lambda (para workers futuros)
  ]
}

# ============================================================================
# CloudWatch Log Group para Inspector Findings
# ============================================================================

resource "aws_cloudwatch_log_group" "inspector" {
  name              = "/aws/inspector/${var.project_name}-${var.environment}"
  retention_in_days = var.environment == "prod" ? 90 : 30

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-inspector-logs"
    }
  )
}

# ============================================================================
# EventBridge Rule para Inspector Findings
# ============================================================================

resource "aws_cloudwatch_event_rule" "inspector_findings" {
  count       = var.enable_alerts ? 1 : 0
  name        = "${var.project_name}-${var.environment}-inspector-findings"
  description = "Capture Inspector findings"

  event_pattern = jsonencode({
    source      = ["aws.inspector2"]
    detail-type = ["Inspector2 Finding"]
    detail = {
      severity = ["HIGH", "CRITICAL"]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "inspector_sns" {
  count     = var.enable_alerts ? 1 : 0
  rule      = aws_cloudwatch_event_rule.inspector_findings[0].name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.guardduty_alerts[0].arn  # Reusar el mismo SNS topic
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
