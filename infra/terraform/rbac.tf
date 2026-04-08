resource "azurerm_role_assignment" "terraform_spi_openai_user" {
  count                = var.assign_current_principal_openai_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "openai_named_users" {
  for_each = toset(var.openai_user_object_ids)

  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "terraform_spi_speech_user" {
  count                = var.enable_speech_deployment && var.assign_current_principal_speech_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.speech[0].id
  role_definition_name = "Cognitive Services Speech User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "terraform_spi_language_user" {
  count                = var.enable_language_deployment && var.assign_current_principal_language_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.language[0].id
  role_definition_name = var.language_role_definition_name
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "language_named_users" {
  for_each = var.enable_language_deployment ? toset(var.language_user_object_ids) : []

  scope                = azurerm_cognitive_account.language[0].id
  role_definition_name = var.language_role_definition_name
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "terraform_spi_translator_user" {
  count                = var.enable_translator_deployment && var.assign_current_principal_translator_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.translator[0].id
  role_definition_name = "Cognitive Services User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "translator_named_users" {
  for_each = var.enable_translator_deployment ? toset(var.translator_user_object_ids) : []

  scope                = azurerm_cognitive_account.translator[0].id
  role_definition_name = "Cognitive Services User"
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "terraform_spi_document_intelligence_user" {
  count                = var.enable_document_intelligence_deployment && var.assign_current_principal_document_intelligence_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.document_intelligence[0].id
  role_definition_name = "Cognitive Services User"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "document_intelligence_named_users" {
  for_each = var.enable_document_intelligence_deployment ? toset(var.document_intelligence_user_object_ids) : []

  scope                = azurerm_cognitive_account.document_intelligence[0].id
  role_definition_name = "Cognitive Services User"
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "terraform_spi_search_service_contributor" {
  count                = var.enable_search_deployment && var.assign_current_principal_search_roles ? 1 : 0
  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Service Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "terraform_spi_search_index_data_contributor" {
  count                = var.enable_search_deployment && var.assign_current_principal_search_roles ? 1 : 0
  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "terraform_spi_search_index_data_reader" {
  count                = var.enable_search_deployment && var.assign_current_principal_search_roles ? 1 : 0
  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Index Data Reader"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "search_named_users_service_contributor" {
  for_each = var.enable_search_deployment ? toset(var.search_user_object_ids) : []

  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Service Contributor"
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "search_named_users_index_data_contributor" {
  for_each = var.enable_search_deployment ? toset(var.search_user_object_ids) : []

  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = each.value
  principal_type       = "User"
}

resource "azurerm_role_assignment" "search_named_users_index_data_reader" {
  for_each = var.enable_search_deployment ? toset(var.search_user_object_ids) : []

  scope                = azurerm_search_service.search[0].id
  role_definition_name = "Search Index Data Reader"
  principal_id         = each.value
  principal_type       = "User"
}
