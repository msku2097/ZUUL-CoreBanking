provider "kubernetes" {
    host                   = azurerm_kubernetes_cluster.zuul_aks.kube_config.0.host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.zuul_aks.kube_config.0.client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.zuul_aks.kube_config.0.client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.zuul_aks.kube_config.0.cluster_ca_certificate)
  }
  
  resource "kubernetes_namespace" "zuul_core" {
    metadata {
      name = "zuul-core"
    }
  }
  
  resource "kubernetes_deployment" "mongodb" {
    metadata {
      name      = "mongodb"
      namespace = kubernetes_namespace.zuul_core.metadata[0].name
    }
    spec {
      replicas = 1
      selector {
        match_labels = {
          app = "mongodb"
        }
      }
      template {
        metadata {
          labels = {
            app = "mongodb"
          }
        }
        spec {
          container {
            name  = "mongodb"
            image = "mongo:latest"
            ports {
              container_port = 27017
            }
          }
        }
      }
    }
  }
  
  resource "kubernetes_service" "mongodb_service" {
    metadata {
      name      = "mongodb-service"
      namespace = kubernetes_namespace.zuul_core.metadata[0].name
    }
    spec {
      selector = {
        app = "mongodb"
      }
      port {
        port        = 27017
        target_port = 27017
      }
      type = "ClusterIP"
    }
  }
  
  # RabbitMQ Deployment
  resource "kubernetes_deployment" "rabbitmq" {
    metadata {
      name      = "rabbitmq"
      namespace = kubernetes_namespace.zuul_core.metadata[0].name
    }
    spec {
      replicas = 1
      selector {
        match_labels = {
          app = "rabbitmq"
        }
      }
      template {
        metadata {
          labels = {
            app = "rabbitmq"
          }
        }
        spec {
          container {
            name  = "rabbitmq"
            image = "rabbitmq:3-management"
            ports {
              container_port = 5672
            }
            ports {
              container_port = 15672
            }
          }
        }
      }
    }
  }
  
  resource "kubernetes_service" "rabbitmq_service" {
    metadata {
      name      = "rabbitmq-service"
      namespace = kubernetes_namespace.zuul_core.metadata[0].name
    }
    spec {
      selector = {
        app = "rabbitmq"
      }
      port {
        port        = 5672
        target_port = 5672
      }
      port {
        port        = 15672
        target_port = 15672
      }
      type = "ClusterIP"
    }
  }
  