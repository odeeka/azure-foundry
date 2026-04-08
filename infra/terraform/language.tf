locals {
  language_account_name = "${var.language_account_name_prefix}-${local.suffix}"
}

resource "azurerm_cognitive_account" "language" {
  count = var.enable_language_deployment ? 1 : 0

  name                          = local.language_account_name
  location                      = azurerm_resource_group.foundry.location
  resource_group_name           = azurerm_resource_group.foundry.name
  kind                          = "TextAnalytics"
  sku_name                      = var.language_sku
  custom_subdomain_name         = local.language_account_name
  public_network_access_enabled = var.public_network_access_enabled
  dynamic_throttling_enabled    = false
  fqdns                         = []

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}