from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, profiles, predictions, documents, external, auth

app = FastAPI(title="PlacementPulse API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(external.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
