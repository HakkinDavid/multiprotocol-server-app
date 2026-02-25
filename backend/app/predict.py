from fastapi import APIRouter
from pydantic import BaseModel
from joblib import load
import pandas as pd

router = APIRouter()

def round_school(x):
    i, f = divmod(x, 1)
    return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    home_goals_half_time: int
    away_goals_half_time: int
    
class PredictResponse(BaseModel):
    home_goals: int
    away_goals: int

model = load("../training/models/best_model_MultiOutputRegressor.joblib")

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Endpoint para predicciones del golizador mexicano
    """
    
    # Preparar los datos de entrada para la predicción
    input_data = pd.DataFrame([{
        'home_team': request.home_team,
        'away_team': request.away_team,
        'home_goals_half_time': request.home_goals_half_time,
        'away_goals_half_time': request.away_goals_half_time
    }])
    
    # Realizar la predicción usando el modelo cargado
    prediction = model.predict(input_data)
    
    return PredictResponse(
        home_goals=round_school(prediction[0][0]),
        away_goals=round_school(prediction[0][1])
    )
