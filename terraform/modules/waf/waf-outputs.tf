# ============================================================================
# WAF Module Outputs
# ============================================================================

output "web_acl_id" {
  description = "ID del Web ACL de WAF"
  value       = aws_wafv2_web_acl.main.id
}

output "web_acl_arn" {
  description = "ARN del Web ACL de WAF"
  value       = aws_wafv2_web_acl.main.arn
}

output "web_acl_capacity" {
  description = "Capacidad utilizada del Web ACL"
  value       = aws_wafv2_web_acl.main.capacity
}

output "log_group_name" {
  description = "Nombre del CloudWatch Log Group para WAF"
  value       = aws_cloudwatch_log_group.waf_logs.name
}
