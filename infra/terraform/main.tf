locals {
  suffix               = random_string.suffix.result
  account_name         = "${var.foundry_account_name_prefix}-${local.suffix}"
  custom_subdomain     = local.account_name
  project_name         = "${var.foundry_project_name_prefix}-${local.suffix}"
  network_default_rule = var.public_network_access_enabled ? "Allow" : "Deny"
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_resource_group" "foundry" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Azure AI Foundry resources: azurerm_cognitive_account with kind = "AIServices" is the
# current recommended Terraform resource for Foundry. azurerm_ai_foundry targets the legacy
# hub-based architecture and is not needed here.
resource "azurerm_cognitive_account" "foundry" {
  name                          = local.account_name
  location                      = azurerm_resource_group.foundry.location
  resource_group_name           = azurerm_resource_group.foundry.name
  kind                          = "AIServices"
  sku_name                      = var.ai_services_sku
  custom_subdomain_name         = local.custom_subdomain
  public_network_access_enabled = var.public_network_access_enabled
  dynamic_throttling_enabled    = false
  fqdns                         = []

  project_management_enabled = true

  identity {
    type = "SystemAssigned"
  }

  network_acls {
    default_action = local.network_default_rule
    ip_rules       = []
  }

  tags = var.tags
}

resource "azurerm_cognitive_account_project" "foundry" {
  name                 = local.project_name
  cognitive_account_id = azurerm_cognitive_account.foundry.id
  location             = azurerm_resource_group.foundry.location
  description          = var.foundry_project_description
  display_name         = var.foundry_project_display_name

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# https://azure.microsoft.com/en-us/pricing/details/azure-openai/
resource "azurerm_cognitive_deployment" "openai" {
  name                       = var.model_deployment_name
  cognitive_account_id       = azurerm_cognitive_account.foundry.id
  rai_policy_name            = "Microsoft.DefaultV2"
  dynamic_throttling_enabled = true

  model {
    format  = "OpenAI"
    name    = var.model_name
    version = var.model_version
  }

  sku {
    name     = var.deployment_sku_name
    capacity = 10
  }
}
