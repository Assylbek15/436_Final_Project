# Digital Document Inspector

Digital Document Inspector is a cloud-deployed document analysis system for scanned PDFs and images. It uses custom YOLO models to detect QR codes and signatures or stamps, exposes the analysis through a FastAPI backend, and provides a React frontend for upload and result viewing.

The current production-oriented setup is:

- detection: local YOLO models in the backend
- storage: Azure Blob Storage for annotated outputs
- hosting: Azure Kubernetes Service (AKS)
- infrastructure: Terraform
- CI/CD: GitHub Actions

## Features

- Upload a PDF or image and analyze it through a web UI
- Run custom YOLO inference on document pages
- Support both single-document and batch ZIP workflows
- Generate annotated page images and an annotated PDF
- Store output artifacts in Azure Blob Storage
- Deploy the stack with Docker, Kubernetes, and Terraform

## Tech Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Uvicorn, Python 3.10
- Detection: Ultralytics YOLOv8, PyTorch
- PDF rendering: PyMuPDF
- Cloud: Azure AKS, ACR, Blob Storage
- IaC: Terraform
- CI/CD: GitHub Actions

## Repository Structure

```text
backend/      FastAPI app, YOLO models, Dockerfile
frontend/     React/Vite app, Dockerfile
k8s/          Kubernetes manifests
terraform/    Azure infrastructure
.github/      GitHub Actions workflow
SETUP.md      Detailed setup instructions
ARCHITECTURE.md  System architecture and design
DEMO_RUNBOOK.md  Pre-demo and recovery commands
```

## Detection Providers

The backend supports three modes through `DETECTION_PROVIDER`:

- `yolo`: force local YOLO models
- `azure`: force Azure Document Intelligence
- `auto`: use Azure only if credentials are present, otherwise fall back to YOLO

For the current cloud deployment, the intended mode is `yolo`.

## Quick Start

### Option 1: Docker Compose

```powershell
docker compose up --build
```

Then open:

- frontend: `http://localhost:3000`
- backend docs: `http://localhost:8000/docs`

### Option 2: Run From Source

1. Clone the repository.
2. Pull the Git LFS model files:

```powershell
git lfs pull
```

3. Start the backend:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

4. Start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Required Environment Variables

Backend configuration is loaded from `backend/.env` locally or from Kubernetes secrets in the cloud.

Common variables:

```env
DETECTION_PROVIDER=yolo
AZURE_DI_ENDPOINT=
AZURE_DI_KEY=
AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
AZURE_STORAGE_CONTAINER=documents
```

## Cloud Deployment Summary

The Azure deployment consists of:

- ACR for container images
- AKS for frontend/backend workloads
- Blob Storage for result persistence
- GitHub Actions for build and deploy automation

Core deployment flow:

1. Terraform provisions Azure resources
2. Docker images are built and pushed to ACR
3. Kubernetes manifests are applied to AKS
4. The ingress exposes the frontend and backend publicly
5. The backend uploads annotated outputs to Blob Storage

For the full procedure, use [SETUP.md](C:/Users/assyl/Digital-Document-Inspector/SETUP.md:1).

## Demo / Live Presentation

If you are presenting the hosted AKS version, use [DEMO_RUNBOOK.md](C:/Users/assyl/Digital-Document-Inspector/DEMO_RUNBOOK.md:1) before the demo. It includes:

- pre-demo health checks
- commands to verify YOLO mode
- recovery steps if the backend crashes
- safe doc-only push commands using `[skip ci]`

## Additional Documentation

- Setup: [SETUP.md](C:/Users/assyl/Digital-Document-Inspector/SETUP.md:1)
- Architecture: [ARCHITECTURE.md](C:/Users/assyl/Digital-Document-Inspector/ARCHITECTURE.md:1)
- Demo operations: [DEMO_RUNBOOK.md](C:/Users/assyl/Digital-Document-Inspector/DEMO_RUNBOOK.md:1)

## Notes

- The YOLO model files are tracked with Git LFS.
- Blob Storage is used for generated artifacts, not for static website hosting.
- Pushing to `main` triggers the GitHub Actions deployment workflow unless you use `[skip ci]`.
