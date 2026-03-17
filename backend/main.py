from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload, documents

app = FastAPI(title="Hackathon IPSSI - Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}
