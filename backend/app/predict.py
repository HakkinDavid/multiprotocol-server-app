from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Define la estructura del body
class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    home_goals_half_time: int
    away_goals_half_time: int
    
class PredictResponse(BaseModel):
    prediction: str
    confidence: float

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Endpoint para predicciones ML
    """
    # Todo: incorporar modelo 
    return PredictResponse(
        prediction="resultado de la predicción",
        confidence=0.95,
    )
