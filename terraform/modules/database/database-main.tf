# ============================================================================
# Database Module - RDS PostgreSQL
# ============================================================================
# Crea una instancia RDS PostgreSQL con:
# - Cifrado con KMS
# - Backups automáticos
# - Multi-AZ (opcional)
# - Schema customizado (app_schema)
# - Security Groups restrictivos
# ============================================================================

# ============================================================================
# DB Subnet Group
# ============================================================================

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.database_subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# ============================================================================
# Security Group para RDS
# ============================================================================

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = var.vpc_id

  # Permitir tráfico desde App Runner
  ingress {
    description     = "PostgreSQL from App Runner"
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  # Salida: PostgreSQL no necesita salida a internet normalmente
  egress {
    description = "Allow all outbound (for maintenance)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-sg"
    }
  )
}

# ============================================================================
# Parameter Group
# ============================================================================

resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-pg-params"
  family = "postgres16"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  # Parámetro estático - requiere reinicio de DB
  parameter {
    name         = "shared_preload_libraries"
    value        = "pg_stat_statements"
    apply_method = "pending-reboot"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-pg-params"
    }
  )
}

# ============================================================================
# RDS Instance
# ============================================================================

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}"

  # Engine
  engine               = "postgres"
  engine_version       = "16.3"
  instance_class       = var.instance_class
  allocated_storage    = var.allocated_storage
  storage_type         = "gp3"
  storage_encrypted    = true
  kms_key_id           = var.kms_key_arn

  # Database
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = var.db_port

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # High Availability
  multi_az = var.multi_az

  # Backups
  backup_retention_period = var.backup_retention
  backup_window           = "03:00-04:00"  # UTC
  maintenance_window      = "mon:04:00-mon:05:00"  # UTC
  skip_final_snapshot     = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = var.environment == "prod" ? 60 : 0
  monitoring_role_arn             = var.environment == "prod" ? aws_iam_role.rds_monitoring[0].arn : null

  # Performance Insights (solo prod)
  performance_insights_enabled    = var.environment == "prod"
  performance_insights_kms_key_id = var.environment == "prod" ? var.kms_key_arn : null
  performance_insights_retention_period = var.environment == "prod" ? 7 : null

  # Parameter Group
  parameter_group_name = aws_db_parameter_group.main.name

  # Auto minor version upgrades
  auto_minor_version_upgrade = var.environment != "prod"

  # Deletion protection (solo prod)
  deletion_protection = var.environment == "prod"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds"
    }
  )

  lifecycle {
    ignore_changes = [
      password,  # Password no debe cambiar en cada apply
      final_snapshot_identifier
    ]
  }
}

# ============================================================================
# IAM Role para Enhanced Monitoring (solo prod)
# ============================================================================

resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.environment == "prod" ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ============================================================================
# Null Resource para ejecutar script de inicialización del schema
# ============================================================================
# NOTA: Este script crea el schema customizado 'app_schema'
# Se ejecuta una sola vez después de crear el RDS

# resource "null_resource" "init_schema" {
#   # Descomentar cuando quieras ejecutar el script de inicialización
#   # Requiere: psql instalado y acceso desde donde ejecutes terraform
#   
#   provisioner "local-exec" {
#     command = <<-EOT
#       PGPASSWORD=${var.db_password} psql -h ${aws_db_instance.main.endpoint} \
#         -U ${var.db_username} -d ${var.db_name} -f ${path.module}/init-schema.sql
#     EOT
#   }
#
#   depends_on = [aws_db_instance.main]
# }
