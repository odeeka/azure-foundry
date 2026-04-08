# https://azure.microsoft.com/en-us/pricing/details/azure-openai/
resource "azurerm_cognitive_deployment" "flux" {
  name                       = "FLUX.1-Kontext-pro"
  cognitive_account_id       = azurerm_cognitive_account.foundry.id
  rai_policy_name            = "Microsoft.DefaultV2"
  dynamic_throttling_enabled = false

  model {
    format  = "Black Forest Labs"
    name    = "FLUX.1-Kontext-pro"
    version = "1"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 20
  }
}

# import {
#   to = azurerm_cognitive_deployment.flux
#   id = "/subscriptions/70dfe42b-7bb7-418d-bcef-0c66090f0ec3/resourceGroups/rg-foundry/providers/Microsoft.CognitiveServices/accounts/foundry-demo-or6zdr/deployments/FLUX.1-Kontext-pro"
# }
