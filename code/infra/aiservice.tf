module "azure_ai_generic" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/aiservice?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location                                             = var.location_aiservice
  location_private_endpoint                            = var.location
  resource_group_name                                  = azurerm_resource_group.resource_group.name
  tags                                                 = var.tags
  cognitive_account_name                               = "${local.prefix}-aig001"
  cognitive_account_kind                               = "CognitiveServices"
  cognitive_account_sku                                = "S0"
  cognitive_account_firewall_bypass_azure_services     = true
  cognitive_account_outbound_network_access_restricted = true
  cognitive_account_outbound_network_access_allowed_fqdns = [
    trimsuffix(trimprefix(module.storage_account.storage_account_primary_blob_endpoint, "https://"), "/"),
    trimsuffix(trimprefix(module.azure_open_ai.cognitive_account_endpoint, "https://"), "/"),
  ]
  cognitive_account_local_auth_enabled  = true
  cognitive_account_deployments         = {}
  diagnostics_configurations            = local.diagnostics_configurations
  subnet_id                             = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds         = 0
  private_dns_zone_id_cognitive_account = var.private_dns_zone_id_cognitive_services
  customer_managed_key                  = local.customer_managed_key
}
