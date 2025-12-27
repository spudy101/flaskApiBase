# ============================================================================
# Lambda Module - Workers (Estructura Base)
# ============================================================================
# Este módulo será utilizado en la siguiente fase para crear workers Lambda.
# Por ahora, solo contiene la estructura básica.
#
# Casos de uso futuros:
# - Procesamiento asíncrono de tareas
# - Scheduled jobs con EventBridge
# - Workers para SQS queues
# - Migrations runner
# ============================================================================

# ============================================================================
# IAM Role para Lambda
# ============================================================================

resource "aws_iam_role" "lambda" {
  count = var.create_lambda ? 1 : 0
  name  = "${var.project_name}-${var.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Policy para CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  count      = var.create_lambda ? 1 : 0
  role       = aws_iam_role.lambda[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Policy para VPC access (si necesita acceder a RDS)
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  count      = var.create_lambda && var.enable_vpc_access ? 1 : 0
  role       = aws_iam_role.lambda[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# ============================================================================
# Security Group para Lambda (si usa VPC)
# ============================================================================

resource "aws_security_group" "lambda" {
  count       = var.create_lambda && var.enable_vpc_access ? 1 : 0
  name        = "${var.project_name}-${var.environment}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = var.vpc_id

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-lambda-sg"
    }
  )
}

# ============================================================================
# CloudWatch Log Group para Lambda Logs
# ============================================================================

resource "aws_cloudwatch_log_group" "lambda" {
  count             = var.create_lambda ? 1 : 0
  name              = "/aws/lambda/${var.project_name}-${var.environment}"
  retention_in_days = var.environment == "prod" ? 30 : 7

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-lambda-logs"
    }
  )
}

# ============================================================================
# NOTA: Lambda Functions se crearán en la siguiente fase
# ============================================================================
# Para crear una función Lambda, descomentar y configurar:
#
# resource "aws_lambda_function" "worker" {
#   filename      = "worker.zip"  # Código del worker
#   function_name = "${var.project_name}-${var.environment}-worker"
#   role          = aws_iam_role.lambda[0].arn
#   handler       = "index.handler"
#   runtime       = "nodejs18.x"
#   timeout       = 300
#   memory_size   = 512
#
#   vpc_config {
#     subnet_ids         = var.private_subnet_ids
#     security_group_ids = [aws_security_group.lambda[0].id]
#   }
#
#   environment {
#     variables = var.environment_variables
#   }
#
#   tags = var.tags
# }
