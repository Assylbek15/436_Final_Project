"""
Application configuration — reads from environment variables.
For local development, copy .env.example to .env and fill in your values.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Azure AI Document Intelligence
# ---------------------------------------------------------------------------
DETECTION_PROVIDER = os.environ.get("DETECTION_PROVIDER", "auto").strip().lower()
AZURE_DI_ENDPOINT = os.environ.get("AZURE_DI_ENDPOINT", "")
AZURE_DI_KEY      = os.environ.get("AZURE_DI_KEY", "")

# ---------------------------------------------------------------------------
# Azure Blob Storage  (used in Step 2)
# ---------------------------------------------------------------------------
AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STORAGE_CONTAINER         = os.environ.get("AZURE_STORAGE_CONTAINER", "documents")

# ---------------------------------------------------------------------------
# Local fallback — YOLO model configs (kept for offline / dev use)
# ---------------------------------------------------------------------------
MODEL_CONFIGS = [
    {
        "path": "./models/qrcode.pt",
        "conf_threshold": 0.65,
        "name": "QR Code Detector",
    },
    {
        "path": "./models/danik.stamp.pt",
        "conf_threshold": 0.25,
        "name": "Signature Detector",
    },
]

# Static output directory
STATIC_DIR = "static/annotated"
