provider "azurerm" {
    features {}
  }
  
  resource "azurerm_resource_group" "zuul_rg" {
    name     = "zuul-core-banking-rg"
    location = "East US"
  }
  
  resource "azurerm_kubernetes_cluster" "zuul_aks" {
    name                = "zuulCoreBankingAKS"
    location            = azurerm_resource_group.zuul_rg.location
    resource_group_name = azurerm_resource_group.zuul_rg.name
    dns_prefix          = "zuulcorebanking"
  
    default_node_pool {
      name       = "default"
      node_count = 2
      vm_size    = "Standard_DS2_v2"
    }
  
    identity {
      type = "SystemAssigned"
    }
  
    network_profile {
      network_plugin = "azure"
    }
  
    tags = {
      environment = "ZuulCoreBanking"
    }
  }
  
  # Output Kubernetes configuration for kubectl
  output "kube_config" {
    value = azurerm_kubernetes_cluster.zuul_aks.kube_config_raw
    sensitive = true
  }
  
  output "cluster_name" {
    value = azurerm_kubernetes_cluster.zuul_aks.name
  }
  