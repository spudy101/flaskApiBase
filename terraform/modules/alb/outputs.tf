output "alb_id" {
  description = "ID del ALB"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "ARN del ALB"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "DNS name del ALB"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID del ALB"
  value       = aws_lb.main.zone_id
}

output "alb_security_group_id" {
  description = "ID del security group del ALB"
  value       = aws_security_group.alb.id
}

output "target_group_arn" {
  description = "ARN del target group"
  value       = aws_lb_target_group.ecs.arn
}

output "http_listener_arn" {
  description = "ARN del HTTP listener"
  value       = aws_lb_listener.http.arn
}

output "https_listener_arn" {
  description = "ARN del HTTPS listener"
  value       = var.certificate_arn != "" ? aws_lb_listener.https[0].arn : null
}

output "logs_bucket_name" {
  description = "Nombre del bucket S3 con logs"
  value       = aws_s3_bucket.alb_logs.id
}
