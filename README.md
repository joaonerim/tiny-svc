# Tiny Service

Just a small Python API that runs on Kubernetes. Nothing fancy.

## What it does

- `GET /healthz` - health check
- `GET /greet?name=something` - says hello
- `GET /metrics` - prometheus stuff

## Run it locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Test:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/greet?name=world
```

## Docker

```bash
docker build -t tiny-service .
docker run -p 8000:8000 tiny-service
```

## Kubernetes

Just run the script:
```bash
./scripts/local-deploy.sh
```

Or do it manually:
```bash
kind create cluster --name tiny-service
docker build -t tiny-service:latest .
kind load docker-image tiny-service:latest --name tiny-service
kubectl create secret generic tiny-service-secret --from-literal=welcome-prefix="$(echo -n 'Hello' | base64)"
kubectl apply -f k8s/
kubectl port-forward service/tiny-service 8080:80
```

## CI stuff

GitHub Actions runs tests/build/scan on every PR. Set `WELCOME_PREFIX` in repo secrets if you want a custom greeting.

Test CI locally with act:
```bash
brew install act
act pull_request --container-architecture linux/amd64 -j test  # for M1/M2 macs
```

## Why ?

**FastAPI** - fast, has automatic docs, better than flask
**Multi-stage docker** - smaller images, less junk in prod.
**kind** - easy local k8s, no cloud needed
**Secret template** - keeps real secrets out of git but shows the structure
**Simple tools** - just flake8 + pytest, lets keep it simple.

## Tests

```bash
source venv/bin/activate
pytest -v
```

## Cleanup

```bash
kind delete cluster --name tiny-service
```
