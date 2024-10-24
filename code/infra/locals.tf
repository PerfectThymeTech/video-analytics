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
    # APPLICATIONINSIGHTS_CONNECTION_STRING = module.application_insights.application_insights_connection_string
    # ApplicationInsightsAgent_EXTENSION_VERSION = "~3"
    # AZURE_SDK_TRACING_IMPLEMENTATION           = "opentelemetry"
    # AZURE_TRACING_ENABLED                      = "true"
    # APPLICATIONINSIGHTS_AUTHENTICATION_STRING = "Authorization=AAD;ClientId=${module.user_assigned_identity.user_assigned_identity_client_id}"
    AZURE_FUNCTIONS_ENVIRONMENT               = "Production"
    AzureWebJobsFeatureFlags                  = "EnableWorkerIndexing"
    AzureWebJobsSecretStorageType             = "keyvault"
    AzureWebJobsSecretStorageKeyVaultUri      = module.key_vault.key_vault_uri
    AzureWebJobsSecretStorageKeyVaultClientId = module.user_assigned_identity.user_assigned_identity_client_id
    FUNCTIONS_WORKER_PROCESS_COUNT            = 2
    SCM_DO_BUILD_DURING_DEPLOYMENT            = "1"
    WEBSITE_OS_TYPE                           = local.service_plan_os_type
    WEBSITE_CONTENTOVERVNET                   = "1"
    MANAGED_IDENTITY_CLIENT_ID                = module.user_assigned_identity.user_assigned_identity_client_id

    # Azure ai service settings
    AZURE_AI_SERVICE_BASE_URL    = module.azure_ai_generic.cognitive_account_endpoint
    AZURE_AI_SERVICE_API_VERSION = "2024-05-01-preview"

    # Azure AI Service config
    AZURE_AI_SPEECH_RESOURCE_ID        = module.azure_ai_speech.cognitive_account_id
    AZURE_AI_SPEECH_BASE_URL           = module.azure_ai_speech.cognitive_account_endpoint # "https://${var.location}.api.cognitive.microsoft.com"
    AZURE_AI_SPEECH_API_VERSION        = "2024-05-15-preview"
    AZURE_AI_SPEECH_PRIMARY_ACCESS_KEY = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.key_vault_secret_azure_ai_speech_cognitive_account_primary_access_key.id})"

    # Azure open ai app settings
    AZURE_OPEN_AI_BASE_URL        = module.azure_open_ai.cognitive_account_endpoint
    AZURE_OPEN_AI_API_VERSION     = "2024-05-01-preview"
    AZURE_OPEN_AI_DEPLOYMENT_NAME = azurerm_cognitive_deployment.cognitive_deployment_gpt_4o.name
    AZURE_OPEN_AI_TEMPERATURE     = "0.0"

    # Blob trigger settings
    BlobTrigger__blobServiceUri  = module.storage_account.storage_account_primary_blob_endpoint
    BlobTrigger__queueServiceUri = module.storage_account.storage_account_primary_queue_endpoint
    BlobTrigger__credential      = "managedidentity"
    BlobTrigger__clientId        = module.user_assigned_identity.user_assigned_identity_client_id

    # Newstagextraction settings
    ROOT_FOLDER_NAME = "newstagextraction"
    SYSTEM_PROMPT    = data.local_file.file_system_prompt.content
    USER_PROMPT      = data.local_file.file_user_prompt.content

    # Storage settings
    STORAGE_DOMAIN_NAME                             = module.storage_account.storage_account_primary_blob_endpoint
    STORAGE_CONTAINER_UPLOAD_NAME                   = local.storage_account_container_upload_name
    STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME          = local.storage_account_container_internal_videos_name
    STORAGE_CONTAINER_INTERNAL_ANALYSIS_SPEECH_NAME = local.storage_account_container_internal_analysis_speech_name
    STORAGE_CONTAINER_INTERNAL_ANALYSIS_VIDEO_NAME  = local.storage_account_container_internal_analysis_video_name
    STORAGE_CONTAINER_RESULTS_NAME                  = local.storage_account_container_results_name
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
  system_prompt_code_path                                 = "${path.module}/../../docs/SystemPrompt.txt"
  user_prompt_code_path                                   = "${path.module}/../../docs/UserPrompt.txt"
  storage_account_container_upload_name                   = "upload-newsvideos"
  storage_account_container_internal_videos_name          = "internal-videos"
  storage_account_container_internal_analysis_speech_name = "internal-analysis-speech"
  storage_account_container_internal_analysis_video_name  = "internal-analysis-video"
  storage_account_container_results_name                  = "results-newsvideos"
  service_plan_os_type                                    = "Linux"
}
