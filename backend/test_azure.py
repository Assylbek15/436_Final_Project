from dotenv import load_dotenv
load_dotenv()

import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ.get("AZURE_DI_ENDPOINT", "")
key      = os.environ.get("AZURE_DI_KEY", "")

print(f"Endpoint : {endpoint}")
print(f"Key      : {key[:8]}...")
print()

pdf_path = r"C:\Users\assyl\Digital-Document-Inspector\pdfs\АПЗ-31 - 1-9-9.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

print(f"File size: {len(pdf_bytes)} bytes")
print("Sending to Azure DI with BARCODES feature enabled...\n")

client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
poller = client.begin_analyze_document(
    "prebuilt-layout",
    body=pdf_bytes,
    content_type="application/pdf",
    features=[DocumentAnalysisFeature.BARCODES],  # <-- this was missing!
)
result = poller.result()

print(f"Pages returned: {len(result.pages or [])}")
for i, page in enumerate(result.pages or []):
    barcodes = page.barcodes or []
    print(f"  Page {i+1}: {len(barcodes)} barcode(s)")
    for b in barcodes:
        print(f"    kind={b.kind}  value={b.value}  confidence={b.confidence}")

total = sum(len(p.barcodes or []) for p in (result.pages or []))
print(f"\nTotal barcodes detected: {total}")
