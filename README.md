# Broken-Cloud
Programming solutions for the Programming on the Cloud course assignments at Concordia University for the Fall 2024 session.

# Microsoft Azure Deployment Steps

## STEP 1: Build and Test the Docker Image Locally
1. Build the Docker image
```bash 
docker build -t nobel-prize-grpc-service .
```

2. Run the Docker container locally
```bash
docker run -p 50051:50051 nobel-prize-grpc-service
```

## STEP 2: Push the Docker Image to Azure Container Registry

1. Create an Azure Container Registry (if you don’t already have one):

```bash
az acr create --resource-group <resource-group> --name <registry-name> --sku Basic
```
2. Login to Azure Container Registry:

```bash
az acr login --name <registry-name>
```
3. Tag and Push the Image to Azure Container Registry:

```bash

docker tag nobel-prize-grpc-service <registry-name>.azurecr.io/nobel-prize-grpc-service:latest

docker push <registry-name>.azurecr.io/nobel-prize-grpc-service:latest
```

