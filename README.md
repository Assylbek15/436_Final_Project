# 🚀 Digital Document Inspector - Deployment Guide

This repository contains the full source code for the Digital Document Inspector.
If you plan to run it directly from GitHub, ensure you first download
the required **model files** from the **GitHub Releases** section and
place them in the expected directories.

For most users---and especially during a hackathon---the **simplest and
most reliable** way to run the system is via **Docker containers**,
preferably on a **macOS (ARM64) machine**, where the images run
natively.


------------------------------------------------------------------------

## 📦 Run via Docker

Both the frontend and backend are published as versioned Docker images.
No local Python, Node, or dependency setup is required.

### **Frontend**

    docker pull alisherkenzhegaliev/innovatex-frontend:v2
    docker run -p 3000:80 alisherkenzhegaliev/innovatex-frontend:v2

Access at: http://localhost:3000

------------------------------------------------------------------------

### **Backend**

    docker pull alisherkenzhegaliev/innovatex-backend:v2
    docker run -p 8000:8000 alisherkenzhegaliev/innovatex-backend:v2

Backend API: http://localhost:8000

------------------------------------------------------------------------

## 🧱 Optional: Run From Source (Requires Models)

If running the application directly from GitHub instead of Docker:

1.  Clone the repo.
2.  Download the required **YOLO/model weights** from GitHub Releases →
    Assets.
3.  Place model files in the correct paths as described in the code.
4.  Install dependencies manually.
5.  Start backend + frontend services.

This method is supported, but less convenient than using the containers.

------------------------------------------------------------------------

## 🧩 Architecture Overview

-   Frontend and backend are deployed as **independent containers**.
-   No shared state; everything communicates through exposed ports.
-   Containers are reproducible and portable across environments.
-   Docker Hub is used as the distribution registry.

------------------------------------------------------------------------

## 📝 Notes

-   macOS systems provide the smoothest experience because the images
    are built natively for ARM64.
-   If running on Windows x86, ensure the image supports
    multi-architecture or use macOS for best compatibility.
-   `docker compose` can orchestrate both containers if needed.
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)

------------------------------------------------------------------------
