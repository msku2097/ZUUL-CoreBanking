
# Zuul Core Banking System - There is only ZUUL...

Wel.. this is a me trying to understand core banking services and how to talk with them. Can I create my own bank with intrest rates calculations and loans operations? A type of playground that if I can build a castle.
I think so... especially in python. Why not learn also GraphQL and talk with RabbitMQ and store at Mongo. This is a very simple service bank structure but it works quite well 


### Functionalities that are implemented:

- Account management - create a new account, view the account, update the account (deposits, withdrawals, loans, payments)
- Transactions - deposit funds,  whithdraw funds, transfer funds, 
- Loans - request one, repay, 
- Intrest calc - calculate and apply to certain products
- History 


## Prerequisites

- Install Azure CLI
- Install Terraform
- Install kubectl
- Install Docker and Docker Compose (for local testing)

Ensure you have an Azure subscription and are logged in using `az login`

## Project Structure

- terraform/: Contains Terraform files for AKS deployment
  - main.tf: AKS resource definitions
  - variables.tf: AKS configuration variables
  - outputs.tf: Cluster output information
  - kubernetes.tf: Kubernetes provider and namespace setup

- kubernetes/: Kubernetes deployment YAML files
  - mongodb-deployment.yaml: MongoDB deployment and service
  - rabbitmq-deployment.yaml: RabbitMQ deployment and service
  - api-deployment.yaml: API deployment and service
  - ui-deployment.yaml: UI deployment and service

- api/: GraphQL API with FastAPI
- ui/: Web UI with Bootstrap
- docker-compose.yml: Docker Compose for local testing
- Dockerfile.*: Dockerfiles for API, ledger, and UI components
- zuul_core_ledger.py: Core banking ledger logic

---

## Deployment on AKS

### Step 1: Terraform Deployment

1. Navigate to the terraform/ directory
2. Initialize Terraform
  ```
  terraform init
  ```
3. Apply Terraform configuration to deploy resources on Azure
  ```
  terraform apply
  ```
  - Review the proposed changes and confirm by typing `yes`
4. Note the output information for the AKS cluster

### Step 2: Configure kubectl to Access AKS Cluster

1. Set up `kubectl` with the AKS cluster credentials
  ```
  az aks get-credentials --resource-group zuul-core-banking-rg --name zuulCoreBankingAKS
  ```
2. Verify connectivity to the AKS cluster
  ```
  kubectl get nodes
  ```

### Step 3: Apply Kubernetes Deployments

1. Navigate to the kubernetes/ directory
2. Apply each YAML file to deploy MongoDB, RabbitMQ, API, and UI
  ```
  kubectl apply -f mongodb-deployment.yaml -n zuul-core
  kubectl apply -f rabbitmq-deployment.yaml -n zuul-core
  kubectl apply -f api-deployment.yaml -n zuul-core
  kubectl apply -f ui-deployment.yaml -n zuul-core
  ```
3. Check the status of all pods to ensure they are running
  ```
  kubectl get pods -n zuul-core
  ```

### Step 4: Expose API and UI Services

1. The API and UI services are set as LoadBalancer type, which will assign external IPs.
2. Get the external IPs for API and UI services
  ```
  kubectl get services -n zuul-core
  ```
3. Access the UI in a browser using the UI service’s external IP. The API can be accessed at `http://<API_EXTERNAL_IP>:8000/graphql`

---

## Running Locally with Docker Compose

1. Ensure Docker is running
2. Navigate to the project root directory
3. Run Docker Compose to start all services locally
  ```
  docker-compose up --build
  ```
4. Access services:
   - UI: `http://localhost:8080`
   - API: `http://localhost:8000/graphql`
5. To stop services, use
  ```
  docker-compose down
  ```

---

## Testing Each Component

### MongoDB

1. In Kubernetes: 
   ```
   kubectl exec -it <mongodb-pod-name> -n zuul-core -- mongo
   ```
2. Locally (Docker):
   ```
   docker exec -it <mongodb-container-id> mongo
   ```
3. Check database status:
   ```
   show dbs
   ```

### RabbitMQ

1. In Kubernetes:
   ```
   kubectl port-forward svc/rabbitmq-service 15672:15672 -n zuul-core
   ```
2. Access RabbitMQ Management Console:
   ```
   http://localhost:15672
   ```
   Default credentials: guest / guest

### API

Well the Rabbit is a pesky creature and API have to wait for him to be available. 
That type of feature 

### UI

1. Access the UI in a browser
   - Kubernetes: `http://<UI_EXTERNAL_IP>`
   - Docker Compose: `http://localhost:8080`
2. Use the UI to perform actions like creating accounts, transferring funds, and viewing transaction history.

### Thanks
Thanks for the people that inspired me