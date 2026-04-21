# ACR
output "acr_login_server" {
  description = "ACR login server URL — use this to push Docker images"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "ACR admin username"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "acr_admin_password" {
  description = "ACR admin password"
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

# AKS
output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "aks_kube_config" {
  description = "AKS kubeconfig — pipe this to ~/.kube/config to connect with kubectl"
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive   = true
}

# Storage
output "storage_connection_string" {
  description = "Azure Blob Storage connection string for the backend .env"
  value       = azurerm_storage_account.storage.primary_connection_string
  sensitive   = true
}

output "storage_container_name" {
  description = "Blob container name"
  value       = azurerm_storage_container.documents.name
}

# Document Intelligence credentials come from your existing resource in the portal.
