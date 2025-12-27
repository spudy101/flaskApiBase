# ============================================================================
# Networking Module
# ============================================================================
# Crea la infraestructura de red completa:
# - VPC
# - Subnets públicas y privadas en múltiples AZs
# - Internet Gateway
# - NAT Gateways (uno por AZ para alta disponibilidad)
# - Route Tables
# - Security Groups base
# ============================================================================

# ============================================================================
# VPC
# ============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc"
    }
  )
}

# ============================================================================
# Internet Gateway
# ============================================================================

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-igw"
    }
  )
}

# ============================================================================
# Subnets Públicas (para NAT Gateways y ALB)
# ============================================================================

resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-public-subnet-${count.index + 1}"
      Type = "public"
    }
  )
}

# ============================================================================
# Subnets Privadas (para RDS y App Runner VPC Connector)
# ============================================================================

resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-private-subnet-${count.index + 1}"
      Type = "private"
    }
  )
}

# ============================================================================
# Elastic IPs para NAT Gateways
# ============================================================================

resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ============================================================================
# NAT Gateways (uno por AZ para alta disponibilidad)
# ============================================================================

resource "aws_nat_gateway" "main" {
  count = min(var.nat_gateway_count, length(var.availability_zones))

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-nat-gateway-${count.index + 1}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ============================================================================
# Route Tables
# ============================================================================

# Route Table para subnets públicas
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-public-rt"
    }
  )
}

# Route Tables para subnets privadas (una por NAT Gateway)
resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    # Usar el NAT correspondiente si existe, sino usar el primero
    nat_gateway_id = aws_nat_gateway.main[min(count.index, var.nat_gateway_count - 1)].id
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
    }
  )
}

# ============================================================================
# Route Table Associations
# ============================================================================

resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ============================================================================
# VPC Endpoints (opcional, para reducir costos de NAT Gateway)
# ============================================================================
# Descomentar si quieres endpoints para S3 y ECR

# resource "aws_vpc_endpoint" "s3" {
#   vpc_id       = aws_vpc.main.id
#   service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
#   
#   tags = merge(
#     var.tags,
#     {
#       Name = "${var.project_name}-${var.environment}-s3-endpoint"
#     }
#   )
# }

# resource "aws_vpc_endpoint_route_table_association" "s3_private" {
#   count           = length(var.availability_zones)
#   route_table_id  = aws_route_table.private[count.index].id
#   vpc_endpoint_id = aws_vpc_endpoint.s3.id
# }
# ============================================================================
# VPC Endpoints para Reducir Costos de NAT Gateway
# ============================================================================
# Agrega esto al módulo networking/main.tf
# 
# Estos endpoints permiten que tus recursos privados (App Runner, Lambda, RDS)
# accedan a servicios AWS sin pasar por el NAT Gateway, reduciendo costos
# de tráfico de datos (~$0.045/GB).
# ============================================================================

# ============================================================================
# 1. S3 Gateway Endpoint (GRATIS)
# ============================================================================
# Para: Subir/descargar archivos de S3, logs, backups
# Costo: $0 (no hay cargo por este endpoint)
# Ahorro: ~$0.045/GB de tráfico S3
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
  
  vpc_endpoint_type = "Gateway"
  
  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id
  )

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-s3-endpoint"
      Service = "S3"
    }
  )
}

# ============================================================================
# 2. DynamoDB Gateway Endpoint (GRATIS)
# ============================================================================
# Para: Si usas DynamoDB en el futuro
# Costo: $0
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  
  vpc_endpoint_type = "Gateway"
  
  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id
  )

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-dynamodb-endpoint"
      Service = "DynamoDB"
    }
  )
}

# ============================================================================
# 3. Secrets Manager Interface Endpoint
# ============================================================================
# Para: Acceder a Secrets Manager sin NAT
# Costo: ~$7.30/mes ($0.01/hora)
# Ahorro: ~$0.045/GB de tráfico + latencia reducida
# Uso: App Runner obtiene credenciales de DB
resource "aws_vpc_endpoint" "secretsmanager" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]
  
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-secretsmanager-endpoint"
      Service = "SecretsManager"
    }
  )
}

# ============================================================================
# 4. ECR (API + DKR) Interface Endpoints
# ============================================================================
# Para: Si usas Docker/ECR para App Runner
# Costo: ~$14.60/mes ($0.01/hora x 2 endpoints)
# Ahorro: Significativo si haces muchos pulls de imágenes
resource "aws_vpc_endpoint" "ecr_api" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.api"
  vpc_endpoint_type   = "Interface"
  
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]
  
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-ecr-api-endpoint"
      Service = "ECR-API"
    }
  )
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]
  
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-ecr-dkr-endpoint"
      Service = "ECR-DKR"
    }
  )
}

# ============================================================================
# 5. CloudWatch Logs Interface Endpoint
# ============================================================================
# Para: Enviar logs de App Runner/Lambda sin NAT
# Costo: ~$7.30/mes
# Ahorro: Depende del volumen de logs
resource "aws_vpc_endpoint" "logs" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.logs"
  vpc_endpoint_type   = "Interface"
  
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]
  
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-logs-endpoint"
      Service = "CloudWatch-Logs"
    }
  )
}

# ============================================================================
# 6. RDS Interface Endpoint (Opcional)
# ============================================================================
# Para: Si necesitas acceder a RDS desde Lambda en otra VPC
# Normalmente no es necesario si RDS y Lambda están en la misma VPC
resource "aws_vpc_endpoint" "rds" {
  count = var.enable_vpc_endpoints && var.enable_rds_endpoint ? 1 : 0

  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.rds"
  vpc_endpoint_type   = "Interface"
  
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]
  
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-endpoint"
      Service = "RDS"
    }
  )
}

# ============================================================================
# Security Group para VPC Endpoints
# ============================================================================
resource "aws_security_group" "vpc_endpoints" {
  count = var.enable_vpc_endpoints ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-vpc-endpoints-"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc-endpoints-sg"
    }
  )
}

# ============================================================================
# Data Source
# ============================================================================
data "aws_region" "current" {}

# ============================================================================
# RESUMEN DE COSTOS
# ============================================================================
# Gateway Endpoints (GRATIS):
# - S3: $0
# - DynamoDB: $0
#
# Interface Endpoints (si enable_vpc_endpoints = true):
# - Secrets Manager: ~$7.30/mes
# - ECR API: ~$7.30/mes
# - ECR DKR: ~$7.30/mes
# - CloudWatch Logs: ~$7.30/mes
# - RDS (opcional): ~$7.30/mes
#
# Total Interface Endpoints: ~$29-36/mes
# 
# AHORRO:
# - Reduce tráfico de NAT Gateway (~$0.045/GB)
# - Si procesas >650GB/mes de tráfico AWS, los endpoints se pagan solos
# - Mejora latencia y seguridad
#
# RECOMENDACIÓN POR AMBIENTE:
# - Dev: Solo Gateway Endpoints (S3, DynamoDB) - GRATIS
# - Staging: Gateway + Secrets Manager + Logs - ~$15/mes
# - Prod: Todos los endpoints - ~$36/mes
# ============================================================================
