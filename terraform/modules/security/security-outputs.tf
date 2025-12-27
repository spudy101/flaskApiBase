# ============================================================================
# Security Module Outputs
# ============================================================================

output "guardduty_detector_id" {
  description = "ID del detector de GuardDuty"
  value       = aws_guardduty_detector.main.id
}

output "guardduty_detector_arn" {
  description = "ARN del detector de GuardDuty"
  value       = aws_guardduty_detector.main.arn
}

output "inspector_account_id" {
  description = "Account ID donde está habilitado Inspector"
  value       = data.aws_caller_identity.current.account_id
}

output "guardduty_log_group" {
  description = "CloudWatch Log Group para GuardDuty"
  value       = aws_cloudwatch_log_group.guardduty.name
}

output "inspector_log_group" {
  description = "CloudWatch Log Group para Inspector"
  value       = aws_cloudwatch_log_group.inspector.name
}

output "alerts_topic_arn" {
  description = "ARN del SNS topic para alertas (si está habilitado)"
  value       = var.enable_alerts ? aws_sns_topic.guardduty_alerts[0].arn : null
}
