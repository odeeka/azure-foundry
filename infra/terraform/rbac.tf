resource "azurerm_role_assignment" "terraform_spi_openai_user" {
  count                = var.assign_current_principal_openai_user_role ? 1 : 0
  scope                = azurerm_cognitive_account.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = data.azurerm_client_config.current.object_id
}
