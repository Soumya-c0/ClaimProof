from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.compile import router as compile_router
from app.api.decide import router as decide_router

app = FastAPI(
    title="ClaimProof API", 
    description="Deterministic rule execution and AI policy compilation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the document upload router
app.include_router(upload_router)
app.include_router(compile_router)
app.include_router(decide_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ClaimProof Core"}