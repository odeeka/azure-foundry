locals {
  translator_account_name = "${var.translator_account_name_prefix}-${local.suffix}"
}

resource "azurerm_cognitive_account" "translator" {
  count = var.enable_translator_deployment ? 1 : 0

  name                          = local.translator_account_name
  location                      = azurerm_resource_group.foundry.location
  resource_group_name           = azurerm_resource_group.foundry.name
  kind                          = "TextTranslation"
  sku_name                      = var.translator_sku
  custom_subdomain_name         = local.translator_account_name
  public_network_access_enabled = var.public_network_access_enabled
  dynamic_throttling_enabled    = false
  fqdns                         = []

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}