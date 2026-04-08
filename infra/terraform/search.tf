locals {
  search_service_name = "${var.search_service_name_prefix}-${local.suffix}"
}

resource "azurerm_search_service" "search" {
  count = var.enable_search_deployment ? 1 : 0

  name                          = local.search_service_name
  resource_group_name           = azurerm_resource_group.foundry.name
  location                      = azurerm_resource_group.foundry.location
  sku                           = var.search_sku
  replica_count                 = var.search_replica_count
  partition_count               = var.search_partition_count
  semantic_search_sku           = var.search_semantic_search_sku
  public_network_access_enabled = var.public_network_access_enabled
  local_authentication_enabled  = var.search_local_authentication_enabled
  authentication_failure_mode   = "http401WithBearerChallenge"

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}