resource "azurerm_role_assignment" "uai_roleassignment_open_ai_contributor" {
  description          = "Required for accessing azure open ai from the function."
  scope                = module.azure_open_ai.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI Contributor"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_cognitive_services_user" {
  description          = "Required for accessing azure ai service from the function."
  scope                = module.azure_ai_generic.cognitive_account_id
  role_definition_name = "Cognitive Services User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_key_vault_secrets_officer" {
  description          = "Required for accessing and storing secrets in the key vault from the function app settings."
  scope                = module.key_vault.key_vault_id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_storage_blob_data_owner" {
  description          = "Required for accessing the storage account for the blob trigger."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "uai_roleassignment_storage_queue_data_contributor" {
  description          = "Required for accessing the storage account for the blob trigger."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# resource "azurerm_role_assignment" "uai_roleassignment_storage_blob_data_contributor" { # Will be ignored, since storage blob data owner permissions have already been granted.
#   description          = "Required for accessing the storage account from the ai service and read/write data."
#   scope                = module.storage_account.storage_account_id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
#   principal_type       = "ServicePrincipal"
# }
