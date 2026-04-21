# Architecture & Pipeline

## What This Is
Digital Document Inspector — a web app that detects QR codes and signatures in PDF/image documents using computer vision models, deployed on Azure Kubernetes Service.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite, served via Nginx |
| Backend | FastAPI (Python 3.10) |
| Detection | YOLO (primary) / Azure AI Document Intelligence (fallback) |
| Storage | Azure Blob Storage |
| Container Registry | Azure Container Registry (ACR) |
| Orchestration | Azure Kubernetes Service (AKS) |
| IaC | Terraform (azurerm ~4.0) |
| CI/CD | GitHub Actions |

---

## Architecture

```
Browser
  │
  ▼
AKS Ingress (nginx / webapprouting.kubernetes.azure.com)
  ├── / → frontend pod (Nginx, port 80)
  ├── /analyze → backend pod (Uvicorn, port 8000)
  ├── /batch-analyze → backend pod
  └── /static → backend pod
            │
            ├── YOLO models (baked into image)
            │     ├── qrcode.pt
            │     └── danik.stamp.pt
            │
            └── Azure Blob Storage
                  └── docinspectortfsa / documents /
                        └── {filename}_{timestamp}/
                              ├── page_1.jpg
                              └── annotated.pdf
```

---

## Azure Resources (provisioned via Terraform)

- **Resource Group**: `doc-inspector-tf-rg` (West US 2)
- **ACR**: `docinspectoracr.azurecr.io` (Basic SKU)
- **AKS**: `docinspector-aks` (1 node, Standard_D2as_v7)
- **Storage Account**: `docinspectortfsa` (LRS, public blob access)
- **Storage Container**: `documents`
- **Document Intelligence**: `doc-inspector-di` (managed manually, F0 tier)

AKS has AcrPull role assigned to pull images from ACR without credentials.

---

## Kubernetes Manifests

| File | Resource |
|---|---|
| `namespace.yaml` | Namespace `doc-inspector` |
| `secret.yaml` | Secret `azure-secrets` (env vars for backend) |
| `backend-deployment.yaml` | Deployment + ClusterIP Service (port 8000) |
| `frontend-deployment.yaml` | Deployment + ClusterIP Service (port 80) |
| `ingress.yaml` | Ingress with path-based routing |
| `hpa.yaml` | HPA: backend 2–6 replicas, frontend 2–4 replicas at 70% CPU |

---

## CI/CD Pipeline (GitHub Actions)

**Trigger**: push or PR to `main`

**Job 1 — Build** (all branches):
1. Checkout code
2. Login to Azure via service principal (`AZURE_CREDENTIALS`)
3. Login to ACR
4. Build & push `backend:latest` and `backend:{sha}`
5. Build & push `frontend:latest` and `frontend:{sha}`

**Job 2 — Deploy** (push to `main` only):
1. Get AKS kubeconfig
2. Apply all K8s manifests (secret generated from GitHub Secrets)
3. Update image tags to current commit SHA
4. Wait for rollout (`kubectl rollout status`)

---

## Detection Flow

```
Upload PDF/Image
      │
      ▼
Backend checks DETECTION_PROVIDER env var
      │
      ├── "yolo" → YOLO models run locally in pod
      └── "azure" (or DI creds set) → Azure Document Intelligence API
                        │
                        ▼
              Annotated image per page
                        │
                        ▼
              Azure Blob Storage upload
                        │
                        ▼
              Public URL returned to frontend
```
