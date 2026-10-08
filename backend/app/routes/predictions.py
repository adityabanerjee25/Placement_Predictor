from fastapi import APIRouter, HTTPException

from app.schemas import PredictionRequest, PredictionResponse
from app.services.predictor import MockPredictor

router = APIRouter()
predictor = MockPredictor()


@router.post("/predictions", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    if not request.confirmed:
        raise HTTPException(status_code=422, detail="Profile must be confirmed before prediction.")
    return predictor.predict(request.profile)
