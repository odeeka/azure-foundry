locals {
  document_intelligence_account_name = "${var.document_intelligence_account_name_prefix}-${local.suffix}"
}

resource "azurerm_cognitive_account" "document_intelligence" {
  count = var.enable_document_intelligence_deployment ? 1 : 0

  name                          = local.document_intelligence_account_name
  location                      = azurerm_resource_group.foundry.location
  resource_group_name           = azurerm_resource_group.foundry.name
  kind                          = "FormRecognizer"
  sku_name                      = var.document_intelligence_sku
  custom_subdomain_name         = local.document_intelligence_account_name
  public_network_access_enabled = var.public_network_access_enabled
  dynamic_throttling_enabled    = false
  fqdns                         = []

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}