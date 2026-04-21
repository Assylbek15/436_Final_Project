import logging
import uuid
import zipfile
import io
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

from app.utils.pdf_tools import pdf_bytes_to_images, images_to_pdf
from app.config import (
    AZURE_DI_ENDPOINT,
    AZURE_DI_KEY,
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_STORAGE_CONTAINER,
    MODEL_CONFIGS,
    STATIC_DIR,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# ---------------------------------------------------------------------------
# Service selection — Azure DI if credentials present, YOLO otherwise
# ---------------------------------------------------------------------------
_USE_AZURE = bool(AZURE_DI_ENDPOINT and AZURE_DI_KEY)
_USE_BLOB  = bool(AZURE_STORAGE_CONNECTION_STRING)

if _USE_AZURE:
    from app.services.azure_document_service import AzureDocumentService
    _azure = AzureDocumentService(AZURE_DI_ENDPOINT, AZURE_DI_KEY)
    log.info("Using Azure Document Intelligence")
else:
    log.info("Azure DI credentials not set — falling back to YOLO")
    import torch
    from app.services.document_inspector import DocumentInspector
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _yolo = DocumentInspector(MODEL_CONFIGS, device=_device, imgsz=1280)

if _USE_BLOB:
    from app.services.azure_blob_service import AzureBlobService
    _blob = AzureBlobService(AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER)
    log.info("Using Azure Blob Storage")
else:
    _blob = None
    log.info("Azure Blob Storage not configured — saving locally")


STATIC_PATH = Path(STATIC_DIR)
STATIC_PATH.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_pdf(pdf_bytes: bytes, rendered_pages: list):
    """Returns list of (detections, annotated_image) per page."""
    if _USE_AZURE:
        return _azure.analyze_pdf(pdf_bytes, rendered_pages)
    # YOLO: process each page independently
    return [_yolo.detect_image(page) for page in rendered_pages]


def _detect_image(pil_image: Image.Image):
    """Returns (detections, annotated_image)."""
    if _USE_AZURE:
        return _azure.analyze_image(pil_image)
    return _yolo.detect_image(pil_image)


def _build_output(job_id: str, page_results: list, page_images: list, filename: str):
    """Turn per-page detection results into the API response dict."""
    job_dir = STATIC_PATH / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    pages_out      = []
    annotated_imgs = []
    total          = 0
    class_stats    = {}
    ann_counter    = 1
    parent_json    = {filename: {}}

    for idx, ((detections, annotated_img), page_img) in enumerate(
        zip(page_results, page_images)
    ):
        annotated_imgs.append(annotated_img)
        img_filename = f"page_{idx + 1}.jpg"

        if _blob:
            img_url = _blob.upload_image(annotated_img, f"{job_id}/{img_filename}")
        else:
            annotated_img.save(job_dir / img_filename)
            img_url = f"/static/annotated/{job_id}/{img_filename}"

        page_w, page_h = page_img.size
        formatted = []
        page_key  = f"page_{idx + 1}"
        parent_json[filename][page_key] = {
            "annotations": [],
            "page_size": {"width": page_w, "height": page_h},
        }

        for det in detections:
            bbox = {
                "x":      det["bbox"][0],
                "y":      det["bbox"][1],
                "width":  det["bbox"][2] - det["bbox"][0],
                "height": det["bbox"][3] - det["bbox"][1],
            }
            formatted.append({
                "category":   det["class"],
                "confidence": det["confidence"],
                "bbox":       bbox,
            })
            class_stats[det["class"]] = class_stats.get(det["class"], 0) + 1
            total += 1

            ann_key = f"annotation_{ann_counter}"
            ann_counter += 1
            parent_json[filename][page_key]["annotations"].append({
                ann_key: {
                    "category": det["class"],
                    "bbox":     bbox,
                    "area":     float(bbox["width"] * bbox["height"]),
                }
            })

        pages_out.append({
            "page_index":           idx + 1,
            "page_size":            {"width": page_w, "height": page_h},
            "detections":           formatted,
            "annotated_image_url":  img_url,
        })

    annotated_pdf_path = str(job_dir / "annotated.pdf")
    images_to_pdf(annotated_imgs, annotated_pdf_path)

    if _blob:
        with open(annotated_pdf_path, "rb") as f:
            pdf_url = _blob.upload_bytes(f.read(), f"{job_id}/annotated.pdf", "application/pdf")
    else:
        pdf_url = f"/static/annotated/{job_id}/annotated.pdf"

    return {
        "job_id":              job_id,
        "pages":               pages_out,
        "annotated_pdf_url":   pdf_url,
        "result":              parent_json,
        "statistics":          {"total_detections": total, "class_statistics": class_stats},
    }


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@router.post("/analyze")
async def analyze(pdf_file: UploadFile = File(...)):
    ext = Path(pdf_file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: PDF, JPG, PNG",
        )

    file_bytes = await pdf_file.read()
    job_id     = uuid.uuid4().hex

    try:
        if ext == ".pdf":
            rendered_pages = pdf_bytes_to_images(file_bytes)
            page_results   = _detect_pdf(file_bytes, rendered_pages)
        else:
            img            = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            rendered_pages = [img]
            page_results   = [_detect_image(img)]

    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        log.exception("Error processing file")
        if "exceeds limit" in msg or "decompression bomb" in msg:
            raise HTTPException(status_code=400, detail="File is too large to process.")
        raise HTTPException(status_code=500, detail=f"Processing error: {msg}")

    output = _build_output(job_id, page_results, rendered_pages, pdf_file.filename)
    return JSONResponse(output)


# ---------------------------------------------------------------------------
# POST /batch-analyze
# ---------------------------------------------------------------------------
@router.post("/batch-analyze")
async def batch_analyze(zip_file: UploadFile = File(...)):
    if not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a ZIP archive")

    zip_bytes = await zip_file.read()

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ZIP file: {e}")

    job_id      = uuid.uuid4().hex
    parent_json = {}
    files_done  = 0
    total       = 0
    class_stats = {}
    ann_counter = 1

    pdf_files = []
    for name in zf.namelist():
        if name.startswith("__MACOSX") or name.startswith("._"):
            continue
        if name.lower().endswith(".pdf"):
            try:
                display = name.encode("cp437").decode("utf-8")
            except (UnicodeDecodeError, UnicodeEncodeError):
                display = name
            pdf_files.append((name, display))

    if not pdf_files:
        raise HTTPException(status_code=400, detail="ZIP contains no PDF files")

    for orig, display in pdf_files:
        try:
            pdf_bytes = zf.read(orig)
        except Exception:
            continue

        try:
            rendered_pages = pdf_bytes_to_images(pdf_bytes)
            page_results   = _detect_pdf(pdf_bytes, rendered_pages)
        except Exception as e:
            msg = str(e)
            parent_json[display] = {
                "error": "PDF too large" if ("exceeds limit" in msg or "decompression bomb" in msg)
                else f"Failed: {msg}"
            }
            continue

        parent_json[display] = {}
        files_done += 1

        for page_idx, ((detections, _), page_img) in enumerate(
            zip(page_results, rendered_pages), start=1
        ):
            w, h      = page_img.size
            page_key  = f"page_{page_idx}"
            parent_json[display][page_key] = {
                "annotations": [],
                "page_size": {"width": w, "height": h},
            }

            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                width  = x2 - x1
                height = y2 - y1
                ann_key = f"annotation_{ann_counter}"
                ann_counter += 1
                parent_json[display][page_key]["annotations"].append({
                    ann_key: {
                        "category": det["class"],
                        "bbox": {"x": x1, "y": y1, "width": width, "height": height},
                        "area": float(width * height),
                    }
                })
                class_stats[det["class"]] = class_stats.get(det["class"], 0) + 1
                total += 1

    return JSONResponse({
        "job_id":          job_id,
        "files_processed": files_done,
        "result":          parent_json,
        "statistics":      {"total_detections": total, "class_statistics": class_stats},
    })
