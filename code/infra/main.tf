resource "azurerm_resource_group" "resource_group" {
  name     = "${local.prefix}-va-rg"
  location = var.location
  tags     = var.tags
}
