# Demo Runbook

Use this file before a live demo so the AKS deployment stays in the working YOLO configuration.

## Before The Demo

```powershell
az aks get-credentials --resource-group doc-inspector-tf-rg --name docinspector-aks --overwrite-existing
kubectl delete hpa -n doc-inspector --all
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl scale deployment/backend -n doc-inspector --replicas=1
kubectl scale deployment/frontend -n doc-inspector --replicas=1
kubectl rollout status deployment/backend -n doc-inspector --timeout=600s
kubectl rollout status deployment/frontend -n doc-inspector --timeout=300s
kubectl get pods -n doc-inspector
kubectl get ingress -n doc-inspector
```

Expected result:

- one `backend` pod is `1/1 Running`
- one `frontend` pod is `1/1 Running`
- backend is using YOLO, not Azure DI

## Verify YOLO Mode

```powershell
kubectl logs -n doc-inspector deployment/backend --tail=100
```

Look for:

```text
Azure DI credentials not set - falling back to YOLO
Using Azure Blob Storage
```

## Smoke Test Before Showing It

```powershell
kubectl logs -n doc-inspector deployment/backend --follow
```

Then open the public app URL and upload one small file. You want to see:

```text
POST /analyze HTTP/1.1" 200 OK
```

## Emergency Recovery

If the site starts returning `502`, backend pods go `CrashLoopBackOff`, or GitHub Actions reapplies a bad config, run:

```powershell
kubectl delete hpa -n doc-inspector --all
kubectl scale deployment/backend -n doc-inspector --replicas=1
kubectl scale deployment/frontend -n doc-inspector --replicas=1
kubectl set resources deployment/backend -n doc-inspector --requests=cpu=250m,memory=1536Mi --limits=cpu=1000m,memory=3Gi
kubectl set env deployment/backend -n doc-inspector YOLO_CONFIG_DIR=/tmp/Ultralytics
kubectl rollout restart deployment/backend -n doc-inspector
kubectl rollout status deployment/backend -n doc-inspector --timeout=600s
kubectl get pods -n doc-inspector
kubectl logs -n doc-inspector deployment/backend --tail=100
```

## If You Only Need To Push Docs

Do not trigger deployment right before the demo. For doc-only pushes:

```powershell
git add README.md ARCHITECTURE.md SETUP.md DEMO_RUNBOOK.md
git commit -m "Update docs [skip ci]"
git push origin main
```

## If You Need To Redeploy The App

```powershell
git add .
git commit -m "Deploy update"
git push origin main
```

Then watch GitHub Actions and verify after deploy:

```powershell
kubectl get pods -n doc-inspector
kubectl logs -n doc-inspector deployment/backend --tail=100
```
