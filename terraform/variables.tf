variable "location" {
    description = "Azure Region"
    default     = "East US"
  }
  
  variable "resource_group_name" {
    description = "Resource Group for AKS Cluster"
    default     = "zuul-core-banking-rg"
  }
  
  variable "cluster_name" {
    description = "AKS Cluster Name"
    default     = "zuulCoreBankingAKS"
  }
  
  variable "node_count" {
    description = "Number of Nodes in AKS Cluster"
    default     = 2
  }
  