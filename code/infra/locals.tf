locals {
  # Naming locals
  prefix = "${lower(var.prefix)}-${var.environment}"
  resource_providers_to_register = [
    "Microsoft.Authorization",
    "Microsoft.CognitiveServices",
    "microsoft.insights",
    "Microsoft.KeyVault",
    "Microsoft.ManagedIdentity",
    "Microsoft.Network",
    "Microsoft.Resources",
    "Microsoft.Web",
  ]

  # Web app locals
  app_settings_default = {
    # Configuration app settings
    APPLICATIONINSIGHTS_CONNECTION_STRING      = module.application_insights.application_insights_connection_string
    ApplicationInsightsAgent_EXTENSION_VERSION = "~3"
    AZURE_SDK_TRACING_IMPLEMENTATION           = "opentelemetry"
    AZURE_TRACING_ENABLED                      = "true"
    AZURE_FUNCTIONS_ENVIRONMENT                = "Production"
    SCM_DO_BUILD_DURING_DEPLOYMENT             = "1"
    WEBSITE_CONTENTOVERVNET                    = "1"

    # Azure ai service settings
    AZURE_AI_SERVICE_BASE_URL    = module.azure_ai_generic.cognitive_account_endpoint
    AZURE_AI_SERVICE_API_VERSION = "2024-05-01-preview"

    # Azure open ai app settings
    AZURE_OPEN_AI_BASE_URL        = module.azure_open_ai.cognitive_account_endpoint
    AZURE_OPEN_AI_API_VERSION     = "2024-05-01-preview"
    AZURE_OPEN_AI_DEPLOYMENT_NAME = azurerm_cognitive_deployment.cognitive_deployment_gpt_4o.name
    AZURE_OPEN_AI_TEMPERATURE     = "0.0"

    # Newstagextraction settings
    NEWSTAGEXTRACTION_ROOT_FOLDER_NAME = "newstagextraction"
    NEWSTAGEXTRACTION_SYSTEM_PROMPT    = data.local_file.file_system_prompt.content
    NEWSTAGEXTRACTION_USER_PROMPT      = data.local_file.file_user_prompt.content

    # Storage settings
    STORAGE_DOMAIN_NAME                      = module.storage_account.storage_account_primary_blob_endpoint
    STORAGE_CONTAINER_UPLOAD_NAME            = local.storage_account_container_upload_name
    STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME   = local.storage_account_container_internal_videos_name
    STORAGE_CONTAINER_INTERNAL_ANALYSIS_NAME = local.storage_account_container_internal_analysis_name
    STORAGE_CONTAINER_RESULTS_NAME           = local.storage_account_container_results_name
  }
  function_app_settings = merge(local.app_settings_default, var.function_app_settings)

  # Resource locals
  virtual_network = {
    resource_group_name = split("/", var.vnet_id)[4]
    name                = split("/", var.vnet_id)[8]
  }
  network_security_group = {
    resource_group_name = split("/", var.nsg_id)[4]
    name                = split("/", var.nsg_id)[8]
  }
  route_table = {
    resource_group_name = split("/", var.route_table_id)[4]
    name                = split("/", var.route_table_id)[8]
  }
  log_analytics_workspace = {
    subscription_id     = split("/", var.log_analytics_workspace_id)[2]
    resource_group_name = split("/", var.log_analytics_workspace_id)[4]
    name                = split("/", var.log_analytics_workspace_id)[8]
  }

  # Logging locals
  diagnostics_configurations = [
    {
      log_analytics_workspace_id = var.log_analytics_workspace_id
      storage_account_id         = ""
    }
  ]

  # CMK locals
  customer_managed_key = null

  # Other locals
  system_prompt_code_path                          = "${path.module}/../../docs/SystemPrompt.txt"
  user_prompt_code_path                            = "${path.module}/../../docs/UserPrompt.txt"
  storage_account_container_upload_name            = "upload-newsvideos"
  storage_account_container_internal_videos_name   = "internal-videos"
  storage_account_container_internal_analysis_name = "internal-analysis"
  storage_account_container_results_name           = "results-newsvideos"
}
