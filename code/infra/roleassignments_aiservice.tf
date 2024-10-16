resource "azurerm_role_assignment" "cognitive_account_roleassignment_storage_blob_data_contributor" {
  description          = "Required for accessing the storage account from the ai service and read/write data."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.azure_ai_generic.cognitive_account_principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "cognitive_account_roleassignment_storage_blob_data_contributor" {
  description          = "Required for accessing the open ai service from the ai service and submit completion API calls."
  scope                = module.azure_open_ai.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.azure_ai_generic.cognitive_account_principal_id
  principal_type       = "ServicePrincipal"
}
