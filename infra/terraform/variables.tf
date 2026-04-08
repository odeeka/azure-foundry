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

variable "openai_user_object_ids" {
  description = "Additional Microsoft Entra user object IDs that should receive the Cognitive Services OpenAI User role on the Foundry account. Useful when Terraform runs as a service principal but local tools run as signed-in users."
  type        = list(string)
  default     = []
}

variable "enable_speech_deployment" {
  description = "Whether to deploy a dedicated Azure AI Speech resource for the speech notebook demo."
  type        = bool
  default     = false
}

variable "speech_account_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Speech account name."
  type        = string
  default     = "foundry-speech"

  validation {
    condition     = can(regex("^[a-z0-9\\-]{3,24}$", var.speech_account_name_prefix))
    error_message = "speech_account_name_prefix must be 3-24 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "speech_sku" {
  description = "SKU for the Azure AI Speech resource. F0 is free tier and S0 is standard."
  type        = string
  default     = "S0"

  validation {
    condition     = contains(["F0", "S0"], var.speech_sku)
    error_message = "speech_sku must be either F0 or S0."
  }
}

variable "assign_current_principal_speech_user_role" {
  description = "Assign the current authenticated principal the Cognitive Services Speech User role on the speech account."
  type        = bool
  default     = true
}

variable "enable_language_deployment" {
  description = "Whether to deploy a dedicated Azure AI Language resource for text analytics tool scenarios."
  type        = bool
  default     = false
}

variable "language_account_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Language account name."
  type        = string
  default     = "foundry-language"

  validation {
    condition     = can(regex("^[a-z0-9\\-]{3,24}$", var.language_account_name_prefix))
    error_message = "language_account_name_prefix must be 3-24 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "language_sku" {
  description = "SKU for the Azure AI Language resource. F0 is free tier and S is standard."
  type        = string
  default     = "S"

  validation {
    condition     = contains(["F0", "S"], var.language_sku)
    error_message = "language_sku must be either F0 or S."
  }
}

variable "assign_current_principal_language_user_role" {
  description = "Assign the current authenticated principal the Cognitive Services User role on the language account."
  type        = bool
  default     = true
}

variable "language_role_definition_name" {
  description = "Built-in RBAC role assigned on the Azure AI Language account for data-plane access. Use a Language-specific role such as Cognitive Services Language Reader, Writer, or Owner."
  type        = string
  default     = "Cognitive Services Language Reader"

  validation {
    condition = contains([
      "Cognitive Services Language Reader",
      "Cognitive Services Language Writer",
      "Cognitive Services Language Owner",
      "Cognitive Services User",
    ], var.language_role_definition_name)
    error_message = "language_role_definition_name must be one of: Cognitive Services Language Reader, Cognitive Services Language Writer, Cognitive Services Language Owner, or Cognitive Services User."
  }
}

variable "language_user_object_ids" {
  description = "Additional Microsoft Entra user object IDs that should receive the Cognitive Services User role on the language account. Useful when Terraform runs as a service principal but local tools run as signed-in users."
  type        = list(string)
  default     = []
}

variable "enable_translator_deployment" {
  description = "Whether to deploy a dedicated Azure AI Translator resource for translation tool scenarios."
  type        = bool
  default     = false
}

variable "translator_account_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Translator account name."
  type        = string
  default     = "foundry-translator"

  validation {
    condition     = can(regex("^[a-z0-9\\-]{3,24}$", var.translator_account_name_prefix))
    error_message = "translator_account_name_prefix must be 3-24 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "translator_sku" {
  description = "SKU for the Azure AI Translator resource. F0 is free tier and S1 is standard."
  type        = string
  default     = "S1"

  validation {
    condition     = contains(["F0", "S1"], var.translator_sku)
    error_message = "translator_sku must be either F0 or S1."
  }
}

variable "assign_current_principal_translator_user_role" {
  description = "Assign the current authenticated principal the Cognitive Services User role on the translator account."
  type        = bool
  default     = true
}

variable "translator_user_object_ids" {
  description = "Additional Microsoft Entra user object IDs that should receive the Cognitive Services User role on the translator account. Useful when Terraform runs as a service principal but local tools run as signed-in users."
  type        = list(string)
  default     = []
}

variable "enable_document_intelligence_deployment" {
  description = "Whether to deploy a dedicated Azure AI Document Intelligence resource for document extraction tool scenarios."
  type        = bool
  default     = false
}

variable "document_intelligence_account_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Document Intelligence account name."
  type        = string
  default     = "foundry-docintel"

  validation {
    condition     = can(regex("^[a-z0-9\\-]{3,24}$", var.document_intelligence_account_name_prefix))
    error_message = "document_intelligence_account_name_prefix must be 3-24 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "document_intelligence_sku" {
  description = "SKU for the Azure AI Document Intelligence resource. F0 is free tier and S0 is standard."
  type        = string
  default     = "S0"

  validation {
    condition     = contains(["F0", "S0"], var.document_intelligence_sku)
    error_message = "document_intelligence_sku must be either F0 or S0."
  }
}

variable "assign_current_principal_document_intelligence_user_role" {
  description = "Assign the current authenticated principal the Cognitive Services User role on the document intelligence account."
  type        = bool
  default     = true
}

variable "document_intelligence_user_object_ids" {
  description = "Additional Microsoft Entra user object IDs that should receive the Cognitive Services User role on the document intelligence account. Useful when Terraform runs as a service principal but local tools run as signed-in users."
  type        = list(string)
  default     = []
}

variable "enable_search_deployment" {
  description = "Whether to deploy a dedicated Azure AI Search service for search and RAG tool scenarios."
  type        = bool
  default     = false
}

variable "search_service_name_prefix" {
  description = "Lowercase alphanumeric prefix used for the Azure AI Search service name."
  type        = string
  default     = "foundry-search"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,24}$", var.search_service_name_prefix))
    error_message = "search_service_name_prefix must be 2-24 characters of lowercase letters, numbers, or hyphens only."
  }
}

variable "search_sku" {
  description = "SKU for the Azure AI Search service. Common values are free, basic, standard, standard2, or standard3."
  type        = string
  default     = "basic"
}

variable "search_replica_count" {
  description = "Replica count for the Azure AI Search service."
  type        = number
  default     = 1
}

variable "search_partition_count" {
  description = "Partition count for the Azure AI Search service."
  type        = number
  default     = 1
}

variable "search_semantic_search_sku" {
  description = "Semantic search plan for the Azure AI Search service. Use free or standard when semantic ranking should be enabled."
  type        = string
  default     = "free"
}

variable "search_local_authentication_enabled" {
  description = "Whether API key based local authentication remains enabled on the Azure AI Search service. Set false to align with Entra ID only notebook scenarios."
  type        = bool
  default     = false
}

variable "assign_current_principal_search_roles" {
  description = "Assign the current authenticated principal the Search Service Contributor, Search Index Data Contributor, and Search Index Data Reader roles on the search service."
  type        = bool
  default     = true
}

variable "search_user_object_ids" {
  description = "Additional Microsoft Entra user object IDs that should receive the required Azure AI Search roles. Useful when Terraform runs as a service principal but local tools run as signed-in users."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Optional tags applied to all resources."
  type        = map(string)
  default     = {}
}

