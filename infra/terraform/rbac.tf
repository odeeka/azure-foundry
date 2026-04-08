resource "azurerm_role_assignment" "terraform_spi_openai_user" {
  count                = var.assign_current_principal_openai_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = data.azurerm_client_config.current.object_id
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
