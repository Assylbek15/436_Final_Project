# Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- Azure CLI (`az`)
- Terraform
- kubectl
- Helm

---

## Local Development (no Docker)

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```
AZURE_DI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_DI_KEY=<your-key>
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_STORAGE_CONTAINER=documents
DETECTION_PROVIDER=yolo   # or "azure"
```

Place YOLO model files in `backend/models/`:
- `qrcode.pt`
- `danik.stamp.pt`

Start server:
```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
VITE_API_BASE=http://localhost:8000
```

```bash
npm run dev
```

UI: http://localhost:5173

---

## Cloud Deployment

### 1. Provision Infrastructure (Terraform)

```bash
az login
cd terraform
terraform init
terraform apply
```

This creates: Resource Group, ACR, AKS, Storage Account, Storage Container.

### 2. Configure AKS

```bash
az aks get-credentials --resource-group doc-inspector-tf-rg --name docinspector-aks --overwrite-existing
az aks approuting enable --resource-group doc-inspector-tf-rg --name docinspector-aks
```

### 3. Build & Push Docker Images

```bash
az acr login --name docinspectoracr

docker build -t docinspectoracr.azurecr.io/backend:latest ./backend
docker push docinspectoracr.azurecr.io/backend:latest

docker build -t docinspectoracr.azurecr.io/frontend:latest ./frontend
docker push docinspectoracr.azurecr.io/frontend:latest
```

### 4. Deploy to Kubernetes

Create `k8s/secret.yaml` (do not commit):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: azure-secrets
  namespace: doc-inspector
type: Opaque
stringData:
  DETECTION_PROVIDER: "yolo"
  AZURE_DI_ENDPOINT: ""
  AZURE_DI_KEY: ""
  AZURE_STORAGE_CONNECTION_STRING: "<your-connection-string>"
  AZURE_STORAGE_CONTAINER: "documents"
```

Apply manifests:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

Get public IP:
```bash
kubectl get ingress -n doc-inspector
```

### 5. CI/CD (GitHub Actions)

Add these secrets to your GitHub repo (`Settings → Secrets → Actions`):

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | JSON from `az ad sp create-for-rbac --sdk-auth` |
| `AZURE_DI_ENDPOINT` | Your Document Intelligence endpoint |
| `AZURE_DI_KEY` | Your Document Intelligence key |
| `AZURE_STORAGE_CONNECTION_STRING` | Your storage connection string |

Create service principal:
```bash
az ad sp create-for-rbac --name "doc-inspector-sp" --role contributor \
  --scopes /subscriptions/<subscription-id> --sdk-auth
```

Push to `main` to trigger the pipeline.

---

## Switching Detection Provider

| Mode | How |
|---|---|
| YOLO (local models) | Set `DETECTION_PROVIDER=yolo` in `.env` or K8s secret |
| Azure DI | Set `DETECTION_PROVIDER=azure` and fill in DI credentials |
| Auto | Leave `DETECTION_PROVIDER=auto` — uses Azure if credentials present |
