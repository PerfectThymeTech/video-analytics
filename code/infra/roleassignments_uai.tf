resource "azurerm_role_assignment" "uai_roleassignment_open_ai_contributor" {
  description          = "Required for accessing azure open ai from the function."
  scope                = module.azure_open_ai.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI Contributor"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_key_vault_secrets_user" {
  description          = "Required for accessing secrets in the key vault from the function app settings."
  scope                = module.key_vault.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_storage_blob_data_contributor" {
  description          = "Required for accessing the storage account from the ai service and read/write data."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}
