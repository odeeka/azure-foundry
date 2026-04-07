output "resource_group_name" {
  description = "Created resource group name."
  value       = azurerm_resource_group.foundry.name
}

output "ai_services_account_name" {
  description = "Azure AI Services account name used by the lab."
  value       = azurerm_cognitive_account.foundry.name
}

output "ai_services_endpoint" {
  description = "Endpoint for the Azure AI Services account."
  value       = azurerm_cognitive_account.foundry.endpoint
}

output "foundry_project_name" {
  description = "Created Foundry project resource name."
  value       = azurerm_cognitive_account_project.foundry.name
}

output "model_deployment_name" {
  description = "Created model deployment name."
  value       = azurerm_cognitive_deployment.openai.name
}

output "foundry_api_key" {
  value     = azurerm_cognitive_account.foundry.primary_access_key
  sensitive = true
}
