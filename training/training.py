import os
from typing import Any
import joblib  # type: ignore[import-untyped]
import pandas as pd

BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
MODEL_DIR: str = os.path.join(BASE_DIR, "models")

def load_model(model_filename: str) -> Any:
    path = os.path.join(MODEL_DIR, model_filename)
    return joblib.load(path)

def predict_match(model: Any, home_team: str, away_team: str, home_ht: float, away_ht: float) -> str:
    X = pd.DataFrame([{
        "home_team": home_team,
        "away_team": away_team,
        "home_goals_half_time": home_ht,
        "away_goals_half_time": away_ht
    }])
    return model.predict(X)[0]

if __name__ == "__main__":
    model_files = [f for f in os.listdir(MODEL_DIR) if f.startswith("best_model_") and f.endswith(".joblib")]
    model_files.sort()
    if not model_files:
        raise SystemExit("No hay modelos en training/models. Corre el notebook primero.")
    model = load_model(model_files[-1])
    pred = predict_match(model, "Club América", "Tigres UANL", 1, 0)
    print(pred)