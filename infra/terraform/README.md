# Terraform Notes

This folder contains the Terraform configuration for the Azure AI Foundry lab environment.

## What It Deploys

By default, the configuration deploys:

- a resource group
- an Azure AI Services account for Foundry
- a Foundry project
- an Azure OpenAI model deployment

It can also optionally deploy dedicated Azure AI Speech, Azure AI Language, Azure AI Translator, Azure AI Document Intelligence, and Azure AI Search resources.

## Optional Speech Deployment

The Speech resource is defined in [infra/terraform/speech.tf](infra/terraform/speech.tf) and is disabled by default.

To enable it, set the following variables in your `terraform.tfvars` file:

```hcl
enable_speech_deployment                = true
speech_account_name_prefix              = "foundryspeech"
speech_sku                              = "S0"
assign_current_principal_speech_user_role = true
```

Related variables are defined in [infra/terraform/variables.tf](infra/terraform/variables.tf).

The Speech resource is created as a dedicated `SpeechServices` cognitive account with:

- a system-assigned managed identity
- a custom subdomain
- public network access controlled by the shared `public_network_access_enabled` variable

The custom subdomain is important for Speech SDK scenarios that use Microsoft Entra ID authentication.

## Optional Language Deployment

The Language resource is defined in [infra/terraform/language.tf](infra/terraform/language.tf) and is disabled by default.

To enable it, set the following variables in your `terraform.tfvars` file:

```hcl
enable_language_deployment                 = true
language_account_name_prefix               = "foundrylanguage"
language_sku                               = "S"
assign_current_principal_language_user_role = true
language_role_definition_name              = "Cognitive Services Language Reader"
language_user_object_ids                   = []
```

Related variables are defined in [infra/terraform/variables.tf](infra/terraform/variables.tf).

The Language resource is created as a dedicated `TextAnalytics` cognitive account with:

- a system-assigned managed identity
- a custom subdomain
- public network access controlled by the shared `public_network_access_enabled` variable

The custom subdomain matters for local SDK scenarios that use Microsoft Entra ID instead of API keys.

If Terraform runs under a service principal but the local Language scripts run under an Azure CLI user, set `language_user_object_ids` to the Microsoft Entra object ID of that user. Terraform will then assign the same Language role to the user as well.

The default Language role is `Cognitive Services Language Reader`, because it explicitly includes the `Microsoft.CognitiveServices/accounts/Language/analyze-text/action` data permission used by the Text Analytics client. You can override this with `language_role_definition_name` if you need a broader role.

## Speech Outputs

When Speech deployment is enabled, Terraform returns these outputs from [infra/terraform/outputs.tf](infra/terraform/outputs.tf):

- `speech_account_name`
- `speech_endpoint`
- `speech_region`
- `speech_resource_id`

These values are the expected inputs for local Python scripts in [tools/README.md](tools/README.md).

## Language Outputs

When Language deployment is enabled, Terraform returns these outputs from [infra/terraform/outputs.tf](infra/terraform/outputs.tf):

- `language_account_name`
- `language_endpoint`
- `language_region`
- `language_resource_id`

These values are the expected inputs for local Language scripts in [tools/README.md](tools/README.md).

## Optional Translator Deployment

The Translator resource is defined in [infra/terraform/translator.tf](infra/terraform/translator.tf) and is disabled by default.

To enable it, set the following variables in your `terraform.tfvars` file:

```hcl
enable_translator_deployment                  = true
translator_account_name_prefix                = "foundrytranslator"
translator_sku                                = "S1"
assign_current_principal_translator_user_role = true
translator_user_object_ids                    = []
```

Related variables are defined in [infra/terraform/variables.tf](infra/terraform/variables.tf).

The Translator resource is created as a dedicated `TextTranslation` cognitive account with:

- a system-assigned managed identity
- a custom subdomain
- public network access controlled by the shared `public_network_access_enabled` variable

The custom subdomain endpoint is important when the local script uses Entra ID and calls the Translator REST API directly instead of using an API key.

## Translator Outputs

When Translator deployment is enabled, Terraform returns these outputs from [infra/terraform/outputs.tf](infra/terraform/outputs.tf):

- `translator_account_name`
- `translator_endpoint` as the custom-domain `https://<account-name>.cognitiveservices.azure.com/` endpoint
- `translator_region`
- `translator_resource_id`

These values are the expected inputs for local Translator scripts in [tools/README.md](tools/README.md).

## Optional Document Intelligence Deployment

The Document Intelligence resource is defined in [infra/terraform/document_intelligence.tf](infra/terraform/document_intelligence.tf) and is disabled by default.

To enable it, set the following variables in your `terraform.tfvars` file:

```hcl
enable_document_intelligence_deployment                  = true
document_intelligence_account_name_prefix                = "foundrydocintel"
document_intelligence_sku                                = "S0"
assign_current_principal_document_intelligence_user_role = true
document_intelligence_user_object_ids                    = []
```

Related variables are defined in [infra/terraform/variables.tf](infra/terraform/variables.tf).

The Document Intelligence resource is created as a dedicated `FormRecognizer` cognitive account with:

- a system-assigned managed identity
- a custom subdomain
- public network access controlled by the shared `public_network_access_enabled` variable

The custom subdomain matters for local SDK scenarios that use `DocumentIntelligenceClient` with Microsoft Entra ID.

If Terraform runs under a service principal but the local Document Intelligence scripts run under an Azure CLI user, set `document_intelligence_user_object_ids` to the Microsoft Entra object ID of that user.

## Document Intelligence Outputs

When Document Intelligence deployment is enabled, Terraform returns these outputs from [infra/terraform/outputs.tf](infra/terraform/outputs.tf):

- `document_intelligence_account_name`
- `document_intelligence_endpoint` as the custom-domain `https://<account-name>.cognitiveservices.azure.com/` endpoint
- `document_intelligence_region`
- `document_intelligence_resource_id`

These values are the expected inputs for local Document Intelligence scripts in [tools/README.md](tools/README.md).

## RBAC

RBAC assignments are defined in [infra/terraform/rbac.tf](infra/terraform/rbac.tf).

Depending on the flags you enable, Terraform can assign the current authenticated principal:

- `Cognitive Services OpenAI User` on the Foundry account
- `Cognitive Services Speech User` on the Speech account
- the role specified by `language_role_definition_name` on the Language account
- `Cognitive Services User` on the Translator account
- `Cognitive Services User` on the Document Intelligence account
- `Search Service Contributor`, `Search Index Data Contributor`, and `Search Index Data Reader` on the Search service

For Language specifically, Terraform can also assign the same Language role to extra Entra users listed in `language_user_object_ids`.
For Translator specifically, Terraform can also assign `Cognitive Services User` to extra Entra users listed in `translator_user_object_ids`.
For Document Intelligence specifically, Terraform can also assign `Cognitive Services User` to extra Entra users listed in `document_intelligence_user_object_ids`.
For Search specifically, Terraform can also assign the three required Search roles to extra Entra users listed in `search_user_object_ids`.
For Azure OpenAI access used by Search RAG scenarios, Terraform can also assign `Cognitive Services OpenAI User` to extra Entra users listed in `openai_user_object_ids`.

## Typical Workflow

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Use [infra/terraform/terraform.tfvars.example](infra/terraform/terraform.tfvars.example) as the starting point for the base Foundry deployment and the optional Speech, Language, Translator, Document Intelligence, and Search deployments.

## Optional Search Deployment

The Search resource is defined in [infra/terraform/search.tf](infra/terraform/search.tf) and is disabled by default.

To enable it, set the following variables in your `terraform.tfvars` file:

```hcl
enable_search_deployment           = true
search_service_name_prefix         = "foundrysearch"
search_sku                         = "basic"
search_replica_count               = 1
search_partition_count             = 1
search_semantic_search_sku         = "free"
search_local_authentication_enabled = false
assign_current_principal_search_roles = true
search_user_object_ids             = []
openai_user_object_ids             = []
```

Related variables are defined in [infra/terraform/variables.tf](infra/terraform/variables.tf).

The Search service is created as a dedicated `azurerm_search_service` resource with:

- semantic search enabled
- local authentication disabled by default for Entra ID aligned notebook scenarios
- public network access controlled by the shared `public_network_access_enabled` variable

The Search notebook also requires Azure OpenAI access for the RAG example. This repository reuses the main Foundry account and model deployment for that part, so you do not need a second OpenAI resource.

## Search Outputs

When Search deployment is enabled, Terraform returns these outputs from [infra/terraform/outputs.tf](infra/terraform/outputs.tf):

- `search_service_name`
- `search_endpoint`
- `search_service_id`
- `search_openai_endpoint`
- `search_openai_deployment_name`

These values map directly to the local Search notebook and script configuration in [tools/README.md](tools/README.md).