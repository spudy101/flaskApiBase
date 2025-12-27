# ⚠️ IMPORTANT: Before reading this README, please read the README in the bootstrap folder first.

# 🚀 Node.js API - AWS Infrastructure with Terraform

[![Terraform](https://img.shields.io/badge/Terraform-1.0+-623CE4?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Production-ready AWS infrastructure for Node.js applications using Terraform with multi-environment support (dev, staging, prod).

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Environment Configuration](#environment-configuration)
- [Deployment](#deployment)
- [Costs](#costs)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project provides a complete, scalable, and production-ready AWS infrastructure for Node.js applications using **Terraform**. It includes:

- **ECS Fargate** for containerized application hosting
- **RDS PostgreSQL** for relational database
- **Cognito** for user authentication
- **ALB** for load balancing
- **ECR** for Docker image registry
- **Multi-environment** setup (dev, staging, prod)
- **Auto-scaling** based on CPU/Memory
- **Security** features (WAF, GuardDuty, Inspector in prod)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Route 53      │ (Optional)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │      WAF        │ (Prod only)
                    └────────┬────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │   Application Load Balancer (ALB)   │
          │     (Public Subnets)                │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      ECS Fargate Service            │
          │   (Private Subnets - Auto Scaling)  │
          │                                     │
          │  ┌─────────┐  ┌─────────┐          │
          │  │ Task 1  │  │ Task 2  │  ...     │
          │  └─────────┘  └─────────┘          │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      RDS PostgreSQL                 │
          │   (Private Subnets - Multi-AZ)      │
          └─────────────────────────────────────┘

External Services:
├── ECR (Docker Registry)
├── Cognito (Authentication)
├── Secrets Manager (Credentials)
├── CloudWatch (Logs & Metrics)
└── KMS (Encryption)
```

---

## ✨ Features

### Core Infrastructure
- ✅ **VPC** with public/private subnets across 2 AZs
- ✅ **NAT Gateways** for private subnet internet access
- ✅ **Internet Gateway** for public subnets
- ✅ **VPC Endpoints** (staging/prod) for AWS services

### Compute
- ✅ **ECS Fargate** - Serverless container orchestration
- ✅ **Auto Scaling** - CPU and memory-based
- ✅ **ECR** - Private Docker image registry
- ✅ **ALB** - Application Load Balancer with health checks

### Database
- ✅ **RDS PostgreSQL** - Managed database
- ✅ **Multi-AZ** deployment (staging/prod)
- ✅ **Automated backups** with configurable retention
- ✅ **Encrypted** storage with KMS

### Security
- ✅ **Cognito** - User pools and identity federation
- ✅ **Secrets Manager** - Secure credential storage
- ✅ **KMS** - Encryption key management
- ✅ **WAF** - Web Application Firewall (prod)
- ✅ **GuardDuty** - Threat detection (prod)
- ✅ **Inspector** - Vulnerability scanning (prod)
- ✅ **Security Groups** - Network access control

### Observability
- ✅ **CloudWatch Logs** - Centralized logging
- ✅ **ALB Access Logs** - Request logging to S3
- ✅ **Container Insights** (prod) - ECS metrics
- ✅ **Lifecycle Policies** - Automatic log cleanup

---

## 📊 Services by Environment

| Service              | Dev | Staging | Prod | Monthly Cost |
|----------------------|-----|---------|------|--------------|
| **Cognito**          | ✅  | ✅      | ✅   | Free*        |
| **ECS Fargate**      | ✅  | ✅      | ✅   | $15-60       |
| **ECR**              | ✅  | ✅      | ✅   | $1-2         |
| **ALB**              | ✅  | ✅      | ✅   | $20          |
| **RDS PostgreSQL**   | ✅  | ✅      | ✅   | $15-50       |
| **Lambda**           | ✅  | ✅      | ✅   | Variable     |
| **Secrets Manager**  | ✅  | ✅      | ✅   | $0.80        |
| **KMS**              | ✅  | ✅      | ✅   | $1           |
| **VPC + NAT**        | ✅  | ✅      | ✅   | $32-64       |
| **VPC Endpoints**    | ❌  | ✅      | ✅   | $7-14        |
| **WAF**              | ❌  | ❌      | ✅   | $5-15        |
| **GuardDuty**        | ❌  | ❌      | ✅   | $5-20        |
| **Inspector**        | ❌  | ❌      | ✅   | $0.15        |

*Up to 50,000 MAUs

---

## 🔧 Prerequisites

### Required Tools
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/) configured
- [Docker](https://www.docker.com/get-started) for building images
- [Git](https://git-scm.com/)

### AWS Account Setup

1. **AWS Account** with appropriate permissions
2. **S3 Bucket** for Terraform state:
   ```bash
   aws s3api create-bucket \
     --bucket nodejs-api-terraform-state-YOUR-ACCOUNT-ID \
     --region us-east-1
   
   aws s3api put-bucket-versioning \
     --bucket nodejs-api-terraform-state-YOUR-ACCOUNT-ID \
     --versioning-configuration Status=Enabled
   ```

3. **DynamoDB Table** for state locking:
   ```bash
   aws dynamodb create-table \
     --table-name nodejs-api-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-1
   ```

4. **GitHub Token** in Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name /nodejs-api/github-token/terraform \
     --secret-string '{"token":"YOUR_GITHUB_PAT"}' \
     --region us-east-1
   ```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/spudy101/nodejsApiBase
cd nodejsApiBase/terraform
```

### 2. Configure Environment

```bash
# Copy example configuration
cp environments/dev/terraform.tfvars.example environments/dev/terraform.tfvars

# Edit with your values
nano environments/dev/terraform.tfvars
```

**Required values:**
```hcl
jwt_secret              = "YOUR_JWT_SECRET"  # Generate: openssl rand -hex 64
github_token_secret_arn = "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:NAME"
```
**Where do I get these values from?**
`jwt_secret`: You can generate it with this command: openssl rand -hex 64

`github_token_secret_arn`: You must create a classic token on GitHub, upload it to AWS Secrets Manager

### 3. Create Dockerfile

In your Node.js project root:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["npm", "start"]
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init -backend-config=environments/dev/backend.hcl

# Review plan
terraform plan -var-file=environments/dev/terraform.tfvars

# Apply changes
terraform apply -var-file=environments/dev/terraform.tfvars
```

### 5. Push Docker Image to ECR

```bash
# Get ECR URL
ECR_URL=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URL

# Build and push
docker build -t nodejs-api .
docker tag nodejs-api:latest $ECR_URL:latest
docker push $ECR_URL:latest

# Force new deployment
aws ecs update-service \
  --cluster nodejs-api-dev \
  --service nodejs-api-dev \
  --force-new-deployment
```

### 6. Access Your Application

```bash
# Get ALB URL
echo "http://$(terraform output -raw alb_dns_name)"
```

---

## 📁 Project Structure

```
terraform/
├── main.tf                      # Root module orchestration
├── variables.tf                 # Root variables
├── outputs.tf                   # Root outputs
├── .terraform.lock.hcl         # Provider version locks
├── .gitignore                  # Git ignore rules
│
├── modules/                     # Reusable modules
│   ├── ecr/                    # Container registry
│   ├── ecs-fargate/           # Container orchestration
│   ├── alb/                   # Load balancer
│   ├── database/              # RDS PostgreSQL
│   ├── cognito/               # Authentication
│   ├── secrets/               # Secrets Manager
│   ├── kms/                   # Encryption keys
│   ├── networking/            # VPC, subnets, NAT
│   ├── lambda/                # Serverless functions
│   ├── waf/                   # Web firewall
│   └── security/              # GuardDuty + Inspector
│
├── environments/               # Per-environment configs
│   ├── dev/
│   │   ├── backend.hcl        # S3 backend config
│   │   ├── terraform.tfvars   # Variables (gitignored)
│   │   └── terraform.tfvars.example
│   ├── staging/
│   │   ├── backend.hcl
│   │   ├── terraform.tfvars
│   │   └── terraform.tfvars.example
│   └── prod/
│       ├── backend.hcl
│       ├── lifecycle.tf       # Deletion protection
│       ├── terraform.tfvars
│       └── terraform.tfvars.example
│
├── scripts/                    # Automation scripts
│   ├── deploy.sh              # Deployment automation
│   ├── validate.sh            # Pre-deployment validation
│   └── push-to-ecr.sh         # ECR image push
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md
    ├── SECURITY.md
    └── RUNBOOK.md
```

---

## ⚙️ Environment Configuration

### Development
- **Purpose**: Active development and testing
- **Cost**: ~$85/month
- **Config**: Minimal (1 NAT, no VPC endpoints, no WAF)
- **RDS**: Single-AZ, db.t3.micro
- **ECS**: 1 task, 0.5 vCPU, 1GB RAM

### Staging
- **Purpose**: Pre-production testing
- **Cost**: ~$120/month
- **Config**: Production-like (1 NAT, VPC endpoints, ALB)
- **RDS**: Multi-AZ, db.t4g.small
- **ECS**: 2 tasks, 1 vCPU, 2GB RAM

### Production
- **Purpose**: Live user traffic
- **Cost**: ~$180/month
- **Config**: Full (2 NATs, VPC endpoints, ALB, WAF, security)
- **RDS**: Multi-AZ, db.t4g.small, 30-day backups
- **ECS**: 2-10 tasks (auto-scaling), 1 vCPU, 2GB RAM

---

## 🚢 Deployment

### Initial Deployment

```bash
# Development
./scripts/deploy.sh dev plan
./scripts/deploy.sh dev apply

# Staging
./scripts/deploy.sh staging plan
./scripts/deploy.sh staging apply

# Production
./scripts/deploy.sh prod plan
./scripts/deploy.sh prod apply
```

### Update Application

```bash
# Build new image
docker build -t nodejs-api:v2.0 .

# Push to ECR
docker tag nodejs-api:v2.0 $ECR_URL:v2.0
docker push $ECR_URL:v2.0

# Update task definition (or use latest tag)
aws ecs update-service \
  --cluster nodejs-api-prod \
  --service nodejs-api-prod \
  --force-new-deployment
```

### Update Infrastructure

```bash
# Review changes
terraform plan -var-file=environments/prod/terraform.tfvars

# Apply updates
terraform apply -var-file=environments/prod/terraform.tfvars
```

### delete Infrastructure

```bash
# destroy
terraform destroy -var-file=environments/dev/terraform.tfvars
```

### Rollback

```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster nodejs-api-prod \
  --service nodejs-api-prod \
  --task-definition nodejs-api-prod:PREVIOUS_REVISION
```

---

## 💰 Costs

### Monthly Estimates (US East 1)

| Environment | Total | Breakdown |
|-------------|-------|-----------|
| **Development** | ~$85 | NAT: $32, ALB: $20, ECS: $15, RDS: $15, Other: $3 |
| **Staging** | ~$120 | NAT: $32, ALB: $20, ECS: $30, RDS: $25, VPC EP: $7, Other: $6 |
| **Production** | ~$180 | NAT: $64, ALB: $20, ECS: $40, RDS: $50, Security: $20, Other: $16 |

### Cost Optimization Tips

- 💡 Use **Reserved Instances** for RDS (save up to 40%)
- 💡 Enable **Savings Plans** for compute (save up to 20%)
- 💡 Review **CloudWatch Logs** retention
- 💡 Delete unused **ECR images** (lifecycle policy included)
- 💡 Use **S3 Intelligent-Tiering** for ALB logs
- 💡 Destroy **dev/staging** when not in use

---

## 🔒 Security

### Best Practices Implemented

- ✅ **Secrets in Secrets Manager** - No hardcoded credentials
- ✅ **KMS encryption** - All data encrypted at rest
- ✅ **Private subnets** - App runs isolated from internet
- ✅ **Security groups** - Least privilege network access
- ✅ **WAF** - Protection against common attacks (prod)
- ✅ **GuardDuty** - Threat detection (prod)
- ✅ **VPC Flow Logs** - Network traffic monitoring
- ✅ **ALB access logs** - Request auditing
- ✅ **IAM roles** - No long-lived credentials

### Security Checklist

- [ ] Rotate secrets regularly
- [ ] Review GuardDuty findings
- [ ] Update base images monthly
- [ ] Review IAM policies quarterly
- [ ] Enable MFA for AWS accounts
- [ ] Review CloudTrail logs
- [ ] Scan containers with Inspector
- [ ] Keep Terraform providers updated

---

## 🔧 Maintenance

### Regular Tasks

**Daily:**
- Monitor CloudWatch dashboards
- Check ECS service health
- Review ALB 5xx errors

**Weekly:**
- Review costs in Cost Explorer
- Check GuardDuty findings
- Update Docker base images

**Monthly:**
- Rotate database passwords
- Update Terraform providers
- Review and clean ECR images
- Backup verification

**Quarterly:**
- Security audit
- Disaster recovery test
- Cost optimization review
- Update dependencies

### Monitoring

```bash
# ECS Service status
aws ecs describe-services \
  --cluster nodejs-api-prod \
  --services nodejs-api-prod

# Check running tasks
aws ecs list-tasks \
  --cluster nodejs-api-prod \
  --service-name nodejs-api-prod

# View logs
aws logs tail /ecs/nodejs-api-prod --follow

# ALB health
aws elbv2 describe-target-health \
  --target-group-arn TARGET_GROUP_ARN
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ECS Tasks Not Starting

```bash
# Check task status
aws ecs describe-tasks \
  --cluster nodejs-api-dev \
  --tasks TASK_ID

# Common causes:
# - Image not in ECR
# - IAM permissions missing
# - Security group blocking traffic
# - Health check failing
```

#### 2. ALB Returns 502/503

```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn TG_ARN

# Common causes:
# - Container not listening on correct port
# - Health check path incorrect
# - Security group blocking ALB → ECS
```

#### 3. Cannot Connect to RDS

```bash
# Verify security group
# RDS SG must allow inbound from ECS SG on port 5432

# Test from ECS task
aws ecs execute-command \
  --cluster nodejs-api-dev \
  --task TASK_ID \
  --container nodejs-api \
  --interactive \
  --command "/bin/sh"

# Inside container:
nc -zv RDS_ENDPOINT 5432
```

#### 4. High Costs

```bash
# Identify cost drivers
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Common causes:
# - NAT Gateway data transfer
# - RDS instance running 24/7
# - ALB with low traffic
# - ECS tasks not scaling down
```
