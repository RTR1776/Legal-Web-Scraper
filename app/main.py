from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="Legal Document System")

# Include all API endpoints.
app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}