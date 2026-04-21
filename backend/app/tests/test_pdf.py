from app.utils.pdf_tools import pdf_bytes_to_images

with open("./static/test_pdf.pdf", "rb") as f:
    pdf_bytes = f.read()

pages = pdf_bytes_to_images(pdf_bytes)

print(f"Pages: {len(pages)}")
for p in pages:
    p.show()# Opens first page for confirmation



# POST -> SAVEPDF
# PDF -> INFERENCE -> OUTPUT
# GET -> GET OUTPUT 

# 2 api call -> handler -> 2 functions