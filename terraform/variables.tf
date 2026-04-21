variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "doc-inspector-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westus2"
}

variable "project_name" {
  description = "Short project name used for naming resources"
  type        = string
  default     = "docinspector"
}

variable "acr_sku" {
  description = "Azure Container Registry SKU"
  type        = string
  default     = "Basic"
}

variable "aks_node_count" {
  description = "Number of AKS nodes"
  type        = number
  default     = 1
}

variable "aks_node_size" {
  description = "AKS node VM size. Start with a burstable SKU to reduce quota and cost pressure."
  type        = string
  default     = "Standard_B2s_v2"
}

variable "storage_account_name" {
  description = "Globally unique storage account name (3-24 chars, lowercase)"
  type        = string
  default     = "docinspectorsa"
}

variable "storage_container_name" {
  description = "Blob container name"
  type        = string
  default     = "documents"
}
