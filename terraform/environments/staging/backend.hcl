# ============================================================================
# Backend Configuration for Staging Environment
# ============================================================================

bucket         = "nodejs-api-terraform-state"
key            = "staging/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "nodejs-api-terraform-locks"
encrypt        = true

skip_region_validation      = false
skip_credentials_validation = false
skip_metadata_api_check     = false
