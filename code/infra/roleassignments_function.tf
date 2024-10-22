resource "azurerm_role_assignment" "function_roleassignment_storage_blob_data_owner" {
  description          = "Required for accessing the storage account from the function host."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_linux_function_app.linux_function_app.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "function_roleassignment_storage_queue_data_contributor" {
  description          = "Required for accessing the storage account for the blob trigger."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Queue Data Contributor"
  principal_id         = azurerm_linux_function_app.linux_function_app.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "function_roleassignment_storage_account_contributor" {
  description          = "Required for accessing the storage account for the blob trigger."
  scope                = module.storage_account.storage_account_id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azurerm_linux_function_app.linux_function_app.identity[0].principal_id
  principal_type       = "ServicePrincipal"
}
