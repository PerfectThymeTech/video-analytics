resource "azurerm_linux_function_app" "linux_function_app" {
  name                = "${local.prefix}-app001"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags
  identity {
    type = "SystemAssigned, UserAssigned"
    identity_ids = [
      module.user_assigned_identity.user_assigned_identity_id
    ]
  }

  app_settings                                   = local.function_app_settings
  builtin_logging_enabled                        = false
  client_certificate_enabled                     = false
  client_certificate_exclusion_paths             = ""
  client_certificate_mode                        = "Required"
  content_share_force_disabled                   = false
  enabled                                        = true
  ftp_publish_basic_authentication_enabled       = false
  functions_extension_version                    = "~4"
  https_only                                     = true
  key_vault_reference_identity_id                = module.user_assigned_identity.user_assigned_identity_id
  public_network_access_enabled                  = false
  storage_account_name                           = module.storage_account.storage_account_name
  storage_uses_managed_identity                  = true
  service_plan_id                                = module.app_service_plan.service_plan_id
  virtual_network_subnet_id                      = azapi_resource.subnet_function.id
  webdeploy_publish_basic_authentication_enabled = false
  site_config {
    always_on                              = true
    api_definition_url                     = null
    api_management_api_id                  = null
    app_command_line                       = null
    app_scale_limit                        = 20
    application_insights_connection_string = module.application_insights.application_insights_connection_string
    application_insights_key               = module.application_insights.application_insights_instrumentation_key
    application_stack {
      python_version = "3.12"
    }
    elastic_instance_minimum          = 1
    ftps_state                        = "Disabled"
    health_check_eviction_time_in_min = 2
    health_check_path                 = var.function_health_check_path
    http2_enabled                     = true
    ip_restriction_default_action     = "Deny"
    load_balancing_mode               = "LeastRequests"
    managed_pipeline_mode             = "Integrated"
    minimum_tls_version               = "1.2"
    pre_warmed_instance_count         = 0
    remote_debugging_enabled          = false
    remote_debugging_version          = null
    runtime_scale_monitoring_enabled  = true
    scm_ip_restriction_default_action = "Deny"
    scm_minimum_tls_version           = "1.2"
    scm_use_main_ip_restriction       = false
    use_32_bit_worker                 = false
    vnet_route_all_enabled            = true
    websockets_enabled                = false
    worker_count                      = 1
  }
}

data "azurerm_monitor_diagnostic_categories" "diagnostic_categories_linux_function_app" {
  resource_id = azurerm_linux_function_app.linux_function_app.id
}

resource "azurerm_monitor_diagnostic_setting" "diagnostic_setting_linux_function_app" {
  name                       = "logAnalytics"
  target_resource_id         = azurerm_linux_function_app.linux_function_app.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.log_analytics_workspace.id

  dynamic "enabled_log" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_linux_function_app.log_category_groups
    content {
      category_group = entry.value
    }
  }

  dynamic "metric" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_linux_function_app.metrics
    content {
      category = entry.value
      enabled  = true
    }
  }
}

resource "azurerm_private_endpoint" "linux_function_app_private_endpoint" {
  name                = "${azurerm_linux_function_app.linux_function_app.name}-pe"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags

  custom_network_interface_name = "${azurerm_linux_function_app.linux_function_app.name}-nic"
  private_service_connection {
    name                           = "${azurerm_linux_function_app.linux_function_app.name}-pe"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_linux_function_app.linux_function_app.id
    subresource_names              = ["sites"]
  }
  subnet_id = azapi_resource.subnet_private_endpoints.id
  dynamic "private_dns_zone_group" {
    for_each = var.private_dns_zone_id_sites == "" ? [] : [1]
    content {
      name = "${azurerm_linux_function_app.linux_function_app.name}-arecord"
      private_dns_zone_ids = [
        var.private_dns_zone_id_sites
      ]
    }
  }

  lifecycle {
    ignore_changes = [
      private_dns_zone_group
    ]
  }
}
