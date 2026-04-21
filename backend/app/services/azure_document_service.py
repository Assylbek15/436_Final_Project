import io
import logging
from typing import List, Dict, Tuple

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.credentials import AzureKeyCredential
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

COLORS = {
    "qr_code":   (0, 0, 255),
    "barcode":   (0, 165, 255),
    "signature": (255, 0, 0),
    "stamp":     (0, 255, 0),
}
DEFAULT_COLOR = (255, 165, 0)


class AzureDocumentService:
    def __init__(self, endpoint: str, api_key: str):
        self.client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(api_key))

    # ------------------------------------------------------------------
    # PDF path — send raw bytes so Azure DI works on the vector content
    # ------------------------------------------------------------------
    def analyze_pdf(
        self,
        pdf_bytes: bytes,
        rendered_pages: List[Image.Image],
    ) -> List[Tuple[List[Dict], Image.Image]]:
        """
        Send the original PDF bytes to Azure DI (best accuracy).
        rendered_pages: already-rendered PIL images used only for annotation drawing.
        Returns a list of (detections, annotated_image) — one entry per page.
        """
        log.info("Sending PDF (%d bytes) to Azure Document Intelligence", len(pdf_bytes))

        poller = self.client.begin_analyze_document(
            "prebuilt-layout",
            body=pdf_bytes,
            content_type="application/pdf",
            features=[DocumentAnalysisFeature.BARCODES],
        )
        result = poller.result()

        log.info("Azure DI returned %d page(s)", len(result.pages or []))

        page_results: List[Tuple[List[Dict], Image.Image]] = []

        for page_idx, az_page in enumerate(result.pages or []):
            if page_idx >= len(rendered_pages):
                break

            pil_image = rendered_pages[page_idx]
            img_w, img_h = pil_image.size

            # Azure DI returns coordinates in INCHES for PDFs.
            # Convert to pixels using the rendered image dimensions as reference.
            az_w = az_page.width  or 1.0   # page width in inches
            az_h = az_page.height or 1.0   # page height in inches

            barcodes = az_page.barcodes or []
            log.info("Page %d: %d barcode(s) found", page_idx + 1, len(barcodes))

            detections: List[Dict] = []
            for barcode in barcodes:
                log.info("  barcode kind=%s confidence=%s polygon=%s",
                         barcode.kind, barcode.confidence, barcode.polygon)
                if not barcode.polygon:
                    continue
                bbox = _inch_polygon_to_pixel_bbox(
                    barcode.polygon, img_w, img_h, az_w, az_h
                )
                kind = "qr_code" if "QR_CODE" in str(barcode.kind).upper() else "barcode"
                detections.append({
                    "class":      kind,
                    "confidence": barcode.confidence if barcode.confidence is not None else 0.90,
                    "bbox":       bbox,
                    "model":      "azure-document-intelligence",
                })

            annotated = _draw_detections(pil_image.copy(), detections)
            page_results.append((detections, annotated))

        return page_results

    # ------------------------------------------------------------------
    # Image path — for JPG / PNG uploads
    # ------------------------------------------------------------------
    def analyze_image(
        self, pil_image: Image.Image
    ) -> Tuple[List[Dict], Image.Image]:
        """Send a single PIL image to Azure DI."""
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        raw = buf.getvalue()

        log.info("Sending image (%d bytes) to Azure Document Intelligence", len(raw))

        poller = self.client.begin_analyze_document(
            "prebuilt-layout",
            body=raw,
            content_type="image/png",
            features=[DocumentAnalysisFeature.BARCODES],
        )
        result = poller.result()

        detections: List[Dict] = []

        if result.pages:
            az_page = result.pages[0]
            img_w, img_h = pil_image.size

            # For images Azure DI returns coordinates in PIXELS
            az_w = az_page.width  or float(img_w)
            az_h = az_page.height or float(img_h)

            barcodes = az_page.barcodes or []
            log.info("Image: %d barcode(s) found", len(barcodes))

            for barcode in barcodes:
                log.info("  barcode kind=%s confidence=%s polygon=%s",
                         barcode.kind, barcode.confidence, barcode.polygon)
                if not barcode.polygon:
                    continue
                # pixel → pixel (scale in case unit differs)
                bbox = _inch_polygon_to_pixel_bbox(
                    barcode.polygon, img_w, img_h, az_w, az_h
                )
                kind = "qr_code" if "QR_CODE" in str(barcode.kind).upper() else "barcode"
                detections.append({
                    "class":      kind,
                    "confidence": barcode.confidence if barcode.confidence is not None else 0.90,
                    "bbox":       bbox,
                    "model":      "azure-document-intelligence",
                })

        annotated = _draw_detections(pil_image.copy(), detections)
        return detections, annotated


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inch_polygon_to_pixel_bbox(
    polygon: List[float],
    px_w: int, px_h: int,
    unit_w: float, unit_h: float,
) -> List[float]:
    """
    polygon: [x0,y0, x1,y1, x2,y2, x3,y3]
    (unit_w, unit_h) can be inches (PDF) or pixels (image) —
    we just scale proportionally to the rendered pixel dimensions.
    """
    xs = [polygon[i] * px_w / unit_w for i in range(0, len(polygon), 2)]
    ys = [polygon[i] * px_h / unit_h for i in range(1, len(polygon), 2)]
    return [min(xs), min(ys), max(xs), max(ys)]


def _draw_detections(image: Image.Image, detections: List[Dict]) -> Image.Image:
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font = ImageFont.load_default()

    for det in detections:
        cls   = det["class"]
        conf  = det["confidence"]
        x1, y1, x2, y2 = det["bbox"]
        color = COLORS.get(cls, DEFAULT_COLOR)

        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)
        label      = f"{cls} {conf:.0%}"
        text_bbox  = draw.textbbox((x1, y1 - 40), label, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x1, y1 - 40), label, fill="white", font=font)

    return image
