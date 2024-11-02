output "kube_config" {
    value = azurerm_kubernetes_cluster.zuul_aks.kube_config_raw
    sensitive = true
  }
  
  output "cluster_name" {
    value = azurerm_kubernetes_cluster.zuul_aks.name
  }
  