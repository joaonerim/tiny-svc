#!/bin/bash

# Simple local deployment script for tiny-service

set -e

echo "Deploying tiny-service locally..."

# Check required tools
for tool in docker kind kubectl; do
    if ! command -v $tool &> /dev/null; then
        echo "ERROR: $tool is not installed"
        exit 1
    fi
done

# Build image
echo "Building Docker image..."
docker build -t tiny-service:latest .

# Test image works
echo "Testing Docker image..."
docker run -d --name test-tiny -p 8081:8000 tiny-service:latest
sleep 5
if curl -f http://localhost:8081/healthz &> /dev/null; then
    echo "Docker image test passed"
else
    echo "ERROR: Docker image test failed"
    exit 1
fi
docker stop test-tiny && docker rm test-tiny

# Always recreate cluster for reliability
CLUSTER_NAME="tiny-service"
echo "Recreating kind cluster..."
kind delete cluster --name $CLUSTER_NAME 2>/dev/null || true
kind create cluster --name $CLUSTER_NAME

# Load image
echo "Loading image into kind..."
kind load docker-image tiny-service:latest --name $CLUSTER_NAME

# Create secret
echo "Creating secret..."
kubectl delete secret tiny-service-secret --ignore-not-found
kubectl create secret generic tiny-service-secret \
    --from-literal=welcome-prefix="${WELCOME_PREFIX:-Hello from local}"

# Deploy
echo "Deploying to Kubernetes..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl rollout status deployment/tiny-service --timeout=120s

# Test deployment
echo "Testing deployment..."
kubectl port-forward service/tiny-service 8080:80 &
PF_PID=$!
sleep 5

curl -s http://localhost:8080/healthz && echo "Health check OK"
curl -s "http://localhost:8080/greet?name=Local" | grep -q "Hello" && echo "Greet endpoint OK"
curl -s http://localhost:8080/metrics | grep -q "http_requests_total" && echo "Metrics endpoint OK"

kill $PF_PID 2>/dev/null || true

echo ""
echo "Deployment complete!"
echo ""
echo "To access the service:"
echo "  kubectl port-forward service/tiny-service 8080:80"
echo "  curl http://localhost:8080/healthz"
echo ""
echo "To cleanup:"
echo "  kind delete cluster --name $CLUSTER_NAME"
