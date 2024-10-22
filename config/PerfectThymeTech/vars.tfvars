# General variables
location           = "northeurope"
location_openai    = "swedencentral"
location_aiservice = "eastus"
environment        = "dev"
prefix             = "vdnlytcs"
tags = {
  workload = "video-analytics"
}

# Service variables
function_app_settings      = {}
function_health_check_path = "/api/v1/heartbeat"

# Logging variables
log_analytics_workspace_id = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-logging-rg/providers/Microsoft.OperationalInsights/workspaces/ptt-dev-log001"

# Network variables
connectivity_delay_in_seconds = 0
vnet_id                       = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/virtualNetworks/spoke-ptt-dev-vnet001"
nsg_id                        = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/networkSecurityGroups/ptt-dev-default-nsg001"
route_table_id                = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/ptt-dev-networking-rg/providers/Microsoft.Network/routeTables/ptt-dev-default-rt001"
subnet_cidr_function          = "10.3.2.64/26"
subnet_cidr_private_endpoints = "10.3.2.128/26"

# DNS variables
private_dns_zone_id_blob               = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net"
private_dns_zone_id_queue              = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.queue.core.windows.net"
private_dns_zone_id_table              = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.table.core.windows.net"
private_dns_zone_id_file               = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.file.core.windows.net"
private_dns_zone_id_vault              = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"
private_dns_zone_id_sites              = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurewebsites.net"
private_dns_zone_id_open_ai            = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.openai.azure.com"
private_dns_zone_id_cognitive_services = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.cognitiveservices.azure.com"
