from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.routers.analyze import router as analyze_router
from fastapi.middleware.cors import CORSMiddleware
from app.config import AZURE_DI_ENDPOINT, AZURE_DI_KEY


app = FastAPI()

origins = [
    "http://localhost:5173",   # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Static files for annotated images
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(analyze_router)


@app.get("/debug-azure")
def debug_azure():
    endpoint = AZURE_DI_ENDPOINT
    key      = AZURE_DI_KEY

    if not endpoint or not key:
        return JSONResponse({
            "status": "ERROR",
            "reason": "Missing credentials",
            "AZURE_DI_ENDPOINT": bool(endpoint),
            "AZURE_DI_KEY": bool(key),
        })

    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
        client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
        models = list(client.list_document_models())
        return JSONResponse({
            "status": "OK",
            "endpoint": endpoint,
            "key_prefix": key[:8] + "...",
            "models_available": len(models),
        })
    except Exception as e:
        return JSONResponse({
            "status": "ERROR",
            "error": str(e),
            "endpoint": endpoint,
            "key_prefix": key[:8] + "..." if key else "",
        })