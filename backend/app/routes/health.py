from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "predictionMode": "mock", "modelVersion": "mock-v1"}
