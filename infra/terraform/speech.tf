locals {
  speech_account_name = "${var.speech_account_name_prefix}-${local.suffix}"
}

resource "azurerm_cognitive_account" "speech" {
  count = var.enable_speech_deployment ? 1 : 0

  name                          = local.speech_account_name
  location                      = azurerm_resource_group.foundry.location
  resource_group_name           = azurerm_resource_group.foundry.name
  kind                          = "SpeechServices"
  sku_name                      = var.speech_sku
  custom_subdomain_name         = local.speech_account_name
  public_network_access_enabled = var.public_network_access_enabled
  dynamic_throttling_enabled    = false
  fqdns                         = []

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}