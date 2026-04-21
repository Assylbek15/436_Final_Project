FROM python:3.10-slim

# Avoid Python buffering logs
ENV PYTHONUNBUFFERED=1

# Azure credentials — injected at runtime via docker run -e or k8s Secret
ENV AZURE_DI_ENDPOINT=""
ENV AZURE_DI_KEY=""
ENV AZURE_STORAGE_CONNECTION_STRING=""
ENV AZURE_STORAGE_CONTAINER="documents"

# Install system dependencies required by:
# - PyMuPDF
# - Pillow
# - OpenCV / YOLO
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies first (better caching)
COPY requirements.txt .

# Install Python packages *without cache*
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY app ./app

# Copy model .pt files
COPY models ./models

# Copy static folder
COPY static ./static

# Expose FastAPI
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
