# ============================================================================
# Production Lifecycle Protection
# ============================================================================
# Este archivo previene la destrucción accidental de recursos críticos
# en el ambiente de producción.
# ============================================================================

# Prevenir destroy de la base de datos
resource "null_resource" "prevent_rds_destroy" {
  lifecycle {
    prevent_destroy = true
  }

  triggers = {
    environment = "prod"
    warning     = "RDS está protegido contra destroy accidental en producción"
  }
}

# NOTA: Para hacer destroy en producción, necesitas:
# 1. Comentar este archivo completo
# 2. terraform apply (para remover la protección)
# 3. terraform destroy (destruir recursos)
#
# Esto es intencional para prevenir destrucciones accidentales.
