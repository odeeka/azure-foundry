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

output "speech_account_name" {
  description = "Azure AI Speech account name when speech deployment is enabled."
  value       = var.enable_speech_deployment ? azurerm_cognitive_account.speech[0].name : null
}

output "speech_endpoint" {
  description = "Endpoint for the Azure AI Speech account when speech deployment is enabled."
  value       = var.enable_speech_deployment ? azurerm_cognitive_account.speech[0].endpoint : null
}

output "speech_region" {
  description = "Azure region for the Azure AI Speech account when speech deployment is enabled."
  value       = var.enable_speech_deployment ? azurerm_cognitive_account.speech[0].location : null
}

output "speech_resource_id" {
  description = "Resource ID for the Azure AI Speech account when speech deployment is enabled."
  value       = var.enable_speech_deployment ? azurerm_cognitive_account.speech[0].id : null
}

output "language_account_name" {
  description = "Azure AI Language account name when language deployment is enabled."
  value       = var.enable_language_deployment ? azurerm_cognitive_account.language[0].name : null
}

output "language_endpoint" {
  description = "Endpoint for the Azure AI Language account when language deployment is enabled."
  value       = var.enable_language_deployment ? azurerm_cognitive_account.language[0].endpoint : null
}

output "language_region" {
  description = "Azure region for the Azure AI Language account when language deployment is enabled."
  value       = var.enable_language_deployment ? azurerm_cognitive_account.language[0].location : null
}

output "language_resource_id" {
  description = "Resource ID for the Azure AI Language account when language deployment is enabled."
  value       = var.enable_language_deployment ? azurerm_cognitive_account.language[0].id : null
}

output "translator_account_name" {
  description = "Azure AI Translator account name when translator deployment is enabled."
  value       = var.enable_translator_deployment ? azurerm_cognitive_account.translator[0].name : null
}

output "translator_endpoint" {
  description = "Custom-domain endpoint for the Azure AI Translator account when translator deployment is enabled. Use this cognitiveservices.azure.com endpoint for document translation and Entra ID based REST calls."
  value       = var.enable_translator_deployment ? "https://${local.translator_account_name}.cognitiveservices.azure.com/" : null
}

output "translator_region" {
  description = "Azure region for the Azure AI Translator account when translator deployment is enabled."
  value       = var.enable_translator_deployment ? azurerm_cognitive_account.translator[0].location : null
}

output "translator_resource_id" {
  description = "Resource ID for the Azure AI Translator account when translator deployment is enabled."
  value       = var.enable_translator_deployment ? azurerm_cognitive_account.translator[0].id : null
}
