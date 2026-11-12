targetScope = 'resourceGroup'

@description('Short lowercase prefix used in globally unique resource names.')
@minLength(3)
@maxLength(12)
param prefix string = 'cupcakeai'

@description('Azure region. Verify Foundry model availability before deployment.')
param location string = resourceGroup().location

@allowed(['dev', 'test', 'prod'])
param environment string = 'dev'

@secure()
@description('SQL administrator password used only for initial provisioning. Replace SQL auth with Entra-only administration before production.')
param sqlAdminPassword string

@description('Enables preview Foundry account and project resources.')
param enableFoundry bool = true

var suffix = uniqueString(subscription().subscriptionId, resourceGroup().id)
var tags = {
  project: 'cup-and-cake-ai'
  environment: environment
  managedBy: 'bicep'
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${prefix}-${environment}'
  location: location
  tags: tags
  properties: {
    retentionInDays: 30
    features: { enableLogAccessUsingOnlyResourcePermissions: true }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${prefix}-${environment}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: take('${prefix}${environment}${suffix}', 24)
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    deleteRetentionPolicy: { enabled: true, days: 7 }
  }
}

resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'documents'
  properties: { publicAccess: 'None' }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: take('kv-${prefix}-${environment}-${suffix}', 24)
  location: location
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: 'sql-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  properties: {
    administratorLogin: 'cupcakeadmin'
    administratorLoginPassword: sqlAdminPassword
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: 'cupcake'
  location: location
  tags: tags
  sku: { name: 'Basic', tier: 'Basic', capacity: 5 }
  properties: {
    zoneRedundant: false
  }
}

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: 'srch-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  sku: { name: 'basic' }
  properties: {
    disableLocalAuth: true
    hostingMode: 'default'
    partitionCount: 1
    replicaCount: 1
    publicNetworkAccess: 'Enabled'
    semanticSearch: 'free'
  }
}

resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'di-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  kind: 'FormRecognizer'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: 'di-${prefix}-${environment}-${suffix}'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource contentSafety 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'cs-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  kind: 'ContentSafety'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: 'cs-${prefix}-${environment}-${suffix}'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource foundry 'Microsoft.CognitiveServices/accounts@2026-07-15-preview' = if (enableFoundry) {
  name: 'ais-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'ais-${prefix}-${environment}-${suffix}'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2026-07-15-preview' = if (enableFoundry) {
  parent: foundry
  name: 'cup-and-cake'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {}
}

resource plan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: 'asp-${prefix}-${environment}'
  location: location
  tags: tags
  sku: { name: 'B1', tier: 'Basic', capacity: 1 }
  kind: 'linux'
  properties: { reserved: true }
}

resource webApp 'Microsoft.Web/sites@2024-11-01' = {
  name: 'app-${prefix}-${environment}-${suffix}'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: true
      ftpsState: 'Disabled'
      linuxFxVersion: 'PYTHON|3.12'
      minTlsVersion: '1.2'
      appCommandLine: 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
      appSettings: [
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
        { name: 'ENABLE_ORYX_BUILD', value: 'true' }
        { name: 'CUPCAKE_ENVIRONMENT', value: environment }
        { name: 'FOUNDRY_PROJECT_ENDPOINT', value: enableFoundry ? 'https://${foundry.name}.services.ai.azure.com/api/projects/${foundryProject.name}' : '' }
      ]
    }
  }
}

output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output foundryProjectEndpoint string = enableFoundry ? 'https://${foundry.name}.services.ai.azure.com/api/projects/${foundryProject.name}' : ''
output searchEndpoint string = 'https://${search.name}.search.windows.net'
output documentIntelligenceEndpoint string = documentIntelligence.properties.endpoint
output storageAccountName string = storage.name
output keyVaultName string = keyVault.name
output sqlServerName string = sqlServer.name

