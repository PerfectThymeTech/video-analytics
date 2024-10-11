resource "azurerm_linux_function_app" "linux_function_app" {
  name                = "${local.prefix}-app001"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags
  identity {
    type = "UserAssigned"
    identity_ids = [
      module.user_assigned_identity.user_assigned_identity_id
    ]
  }

  app_settings                             = local.function_app_settings
  builtin_logging_enabled                  = false
  client_certificate_enabled               = false
  client_certificate_exclusion_paths       = ""
  client_certificate_mode                  = "Required"
  content_share_force_disabled             = false
  enabled                                  = true
  ftp_publish_basic_authentication_enabled = false
  functions_extension_version              = "~4"
  https_only                               = true
  key_vault_reference_identity_id          = module.user_assigned_identity.user_assigned_identity_id
  public_network_access_enabled = false
  storage_account_name = module.storage_account.storage_account_name
  storage_uses_managed_identity = true
  service_plan_id                                = module.app_service_plan.service_plan_id
  virtual_network_subnet_id                      = azapi_resource.subnet_function.id
  webdeploy_publish_basic_authentication_enabled = false
  site_config {
    always_on = true
    api_definition_url    = null
    api_management_api_id = null
    app_command_line = null
    app_scale_limit = 20
    application_insights_connection_string = module.application_insights.application_insights_connection_string
    application_insights_key = module.application_insights.application_insights_instrumentation_key
    application_stack {
      python_version = "3.12"
    }
    elastic_instance_minimum = 1
    ftps_state = "Disabled"
    health_check_eviction_time_in_min = 2
    health_check_path = var.function_health_check_path
    http2_enabled = true
    ip_restriction_default_action = "Deny"
    load_balancing_mode = "LeastRequests"
    managed_pipeline_mode = "Integrated"
    minimum_tls_version = "1.2"
    pre_warmed_instance_count = 0
    remote_debugging_enabled = false
    remote_debugging_version = null
    runtime_scale_monitoring_enabled = true
    scm_ip_restriction_default_action = "Deny"
    scm_minimum_tls_version = "1.2"
    scm_use_main_ip_restriction = false
    use_32_bit_worker = false
    vnet_route_all_enabled = true
    websockets_enabled = false
    worker_count = 1
  }
}
