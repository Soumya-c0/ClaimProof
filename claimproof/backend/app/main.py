from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import compile, decide, prove, upload

app = FastAPI(title="ClaimProof API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(compile.router)
app.include_router(decide.router)
app.include_router(prove.router)


@app.get("/health")
def health():
    return {"status": "ok"}