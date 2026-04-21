import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
from typing import List

# Increase PIL's image size limit to handle large PDFs
# Default is ~178 million pixels, we increase it to 500 million
Image.MAX_IMAGE_PIXELS = 500_000_000


def pdf_bytes_to_images(pdf_bytes: bytes, max_dimension: int = 2048):
    """
    Convert PDF bytes into a list of PIL Images (one per page).
    
    Args:
        pdf_bytes: PDF file as bytes
        max_dimension: Maximum width/height in pixels (default 2048)
                      This prevents excessive memory usage while maintaining quality
    """
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    images = []
    for page_index in range(len(pdf)):
        page = pdf.load_page(page_index)
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Calculate appropriate DPI to keep within max_dimension
        # Default DPI is 72, we scale it to fit within max_dimension
        scale_width = max_dimension / page_width
        scale_height = max_dimension / page_height
        scale = min(scale_width, scale_height, 2.8)  # Cap at ~200 DPI (2.8x scale)
        
        # Render page with calculated scale
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        images.append(image)

    pdf.close()
    return images



def images_to_pdf(images: List[Image.Image], output_path: str):
    """
    Convert a list of PIL images into a single PDF file at output_path.
    """
    if not images:
        raise ValueError("No images supplied for PDF export")

    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Convert all images to RGB and save as PDF
    rgb_images = [img.convert("RGB") for img in images]

    # First image saves the PDF, others get appended
    rgb_images[0].save(output_path, save_all=True, append_images=rgb_images[1:])

    return output_path
