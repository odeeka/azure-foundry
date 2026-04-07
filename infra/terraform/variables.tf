variable "client_id" {
  type        = string
  description = "Client ID for Azure authentication. Optional when using az login or managed identity."
}

variable "client_secret" {
  type = string
}

variable "tenant_id" {
  type        = string
  description = "Tenant ID for Azure authentication. Optional when using az login or managed identity."
}

variable "subscription_id" {
  type = string
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the lab resource group."
  type        = string
  default     = "rg-ai-foundry-lab"
}

variable "ai_services_sku" {
  description = "SKU for the Azure AI Services account backing Azure AI Foundry."
  type        = string
  default     = "S0"
}

variable "foundry_account_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Services account name."
  type        = string
  default     = "foundry-demo"

  validation {
    condition     = can(regex("^[a-z0-9\\-]{3,18}$", var.foundry_account_name_prefix))
    error_message = "foundry_account_name_prefix must be 3-18 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "foundry_project_name_prefix" {
  description = "Prefix used for the Foundry project resource name."
  type        = string
  default     = "foundry-demo"
}

variable "foundry_project_display_name" {
  description = "Display name shown for the Foundry project."
  type        = string
  default     = "foundry-demo"
}

variable "foundry_project_description" {
  description = "Description for the Foundry project."
  type        = string
  default     = "Demo project for Azure AI Foundry."
}

variable "model_deployment_name" {
  description = "Name of the Azure OpenAI model deployment."
  type        = string
  default     = "example-cd"
}

variable "model_name" {
  description = "Model name to deploy. Availability depends on region and subscription."
  type        = string
  default     = "gpt-4.1-mini"
}

variable "model_version" {
  description = "Model version to deploy. Availability depends on region and subscription."
  type        = string
  default     = "2025-04-14"
}

variable "deployment_sku_name" {
  description = "SKU name for the cognitive deployment."
  type        = string
  default     = "Standard"
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled for the Azure AI Services account."
  type        = bool
  default     = true
}

variable "assign_current_principal_openai_user_role" {
  description = "Assign the current authenticated principal the Cognitive Services OpenAI User role on the account."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Optional tags applied to all resources."
  type        = map(string)
  default     = {}
}

