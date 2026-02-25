import os
import glob
from typing import Any
import numpy as np
import joblib  # type: ignore[import-untyped]
import pandas as pd

BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
MODEL_DIR: str = os.path.join(BASE_DIR, "models")

# Para correr con los modelos en terminacion "_test" se utiliza
# el argumento --test al ejecutar el script:
#   python training.py --test

def find_latest_model(test: bool = False) -> str:
    """Busca el modelo exportado mas reciente en MODEL_DIR.

    Parametros
    ----------
    test : bool
        Si es True, busca modelos de prueba con el sufijo '_test.joblib'
        (generados por la Seccion 15 del notebook).
        Si es False, busca el modelo ganador definitivo sin ese sufijo
        (generado por la Seccion 14 del notebook).

    El archivo devuelto es el modificado mas recientemente dentro del
    patron correspondiente, para reflejar el ultimo entrenamiento ejecutado.
    """
    if test:
        pattern = os.path.join(MODEL_DIR, "best_model_*_test.joblib")
    else:
        # Patron definitivo: excluye archivos con sufijo _test
        pattern = os.path.join(MODEL_DIR, "best_model_*.joblib")

    candidates = glob.glob(pattern)

    if not test:
        # Excluimos los archivos de prueba para quedarnos solo con el ganador.
        candidates = [c for c in candidates if not c.endswith("_test.joblib")]

    if not candidates:
        kind = "de prueba (_test)" if test else "definitivo"
        raise FileNotFoundError(
            f"No se encontro ningun modelo {kind} en '{MODEL_DIR}'. "
            "Ejecuta el notebook training.ipynb primero."
        )

    # Ordenamos por fecha de modificacion y tomamos el mas reciente.
    return max(candidates, key=os.path.getmtime)


def load_model(model_path: str | None = None, test: bool = False) -> Any:
    """Carga un modelo serializado con joblib.

    Parametros
    ----------
    model_path : str | None
        Ruta completa al archivo .joblib. Si es None, se busca automaticamente
        el modelo mas reciente segun el valor de 'test'.
    test : bool
        Si es True, busca modelos de prueba con sufijo '_test.joblib'.
        Ignorado cuando se proporciona 'model_path' directamente.
    """
    if model_path is None:
        model_path = find_latest_model(test=test)
    return joblib.load(model_path)


def _is_multioutput(raw: np.ndarray) -> bool:
    """Determina si la salida del modelo corresponde a un regresor multi-salida.

    El regresor multi-salida devuelve un array 2-D de forma (n_samples, 2)
    con los goles predichos (home, away) como valores numericos continuos.
    Los clasificadores devuelven un array 1-D de etiquetas ('H', 'A', 'D').
    """
    arr = np.asarray(raw)
    return arr.ndim == 2 and arr.shape[1] == 2 and np.issubdtype(arr.dtype, np.number)


def _goals_to_result(home_goals: float, away_goals: float) -> str:
    """Deriva el resultado del partido a partir de los goles predichos.

    Redondea al entero mas cercano y recorta a 0 para evitar goles negativos.
    """
    h = max(0, round(home_goals))
    a = max(0, round(away_goals))
    if h > a:
        return "H"
    elif h < a:
        return "A"
    return "D"


def predict_match(
    model: Any,
    home_team: str,
    away_team: str,
    home_ht: float,
    away_ht: float,
) -> dict[str, Any]:
    """Genera una prediccion para un partido dado el estado al medio tiempo.

    Retorna un diccionario con:
        - result    : resultado predicho ('H', 'A' o 'D')
        - home_goals: goles predichos del equipo local  (solo para regresor multi-salida)
        - away_goals: goles predichos del equipo visitante (solo para regresor multi-salida)
        - model_type: tipo de modelo utilizado ('classifier' o 'multioutput_regressor')
    """
    X = pd.DataFrame([{
        "home_team": home_team,
        "away_team": away_team,
        "home_goals_half_time": home_ht,
        "away_goals_half_time": away_ht,
    }])

    raw = model.predict(X)

    if _is_multioutput(raw):
        home_goals = float(raw[0, 0])
        away_goals = float(raw[0, 1])
        result = _goals_to_result(home_goals, away_goals)
        return {
            "result": result,
            "home_goals": max(0, round(home_goals)),
            "away_goals": max(0, round(away_goals)),
            "model_type": "multioutput_regressor",
        }
    else:
        return {
            "result": str(raw[0]),
            "home_goals": None,
            "away_goals": None,
            "model_type": "classifier",
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prediccion de partidos con el modelo entrenado.")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Carga los tres modelos de prueba (sufijo _test.joblib) y compara sus predicciones.",
    )
    args = parser.parse_args()

    # Datos de entrada para la prediccion de prueba.
    home_team  = "Club America"
    away_team  = "Tigres UANL"
    home_ht    = 1
    away_ht    = 0

    def print_input() -> None:
        """Imprime los datos de entrada utilizados en la prediccion."""
        print(f"  Equipo local     : {home_team}")
        print(f"  Equipo visitante : {away_team}")
        print(f"  Goles HT local   : {home_ht}")
        print(f"  Goles HT visita  : {away_ht}")

    def print_prediction(prediction: dict) -> None:
        """Imprime el resultado de la prediccion."""
        print(f"  Resultado        : {prediction['result']}")
        if prediction["model_type"] == "multioutput_regressor":
            print(f"  Goles predichos  : {prediction['home_goals']} - {prediction['away_goals']}")
        print(f"  Tipo de modelo   : {prediction['model_type']}")

    if args.test:
        # Cargamos los tres modelos de prueba y ejecutamos una prediccion con cada uno.
        test_models = [
            "best_model_LogisticRegression_test.joblib",
            "best_model_RandomForest_test.joblib",
            "best_model_MultiOutputRegressor_test.joblib",
        ]

        print("=" * 55)
        print("COMPARACION DE MODELOS DE PRUEBA")
        print("=" * 55)

        for filename in test_models:
            model_path = os.path.join(MODEL_DIR, filename)
            if not os.path.exists(model_path):
                print(f"\n[OMITIDO] {filename} no encontrado.")
                continue

            model = load_model(model_path)
            prediction = predict_match(model, home_team, away_team, home_ht, away_ht)

            print(f"\nModelo           : {filename}")
            print_input()
            print_prediction(prediction)

        print("\n" + "=" * 55)

    else:
        # Carga automatica del modelo definitivo mas reciente (Seccion 14 del notebook).
        model_path = find_latest_model(test=False)

        model = load_model(model_path)
        prediction = predict_match(model, home_team, away_team, home_ht, away_ht)

        print("=" * 55)
        print("PREDICCION - MODELO DEFINITIVO")
        print("=" * 55)
        print(f"\nModelo           : {os.path.basename(model_path)}")
        print_input()
        print_prediction(prediction)
        print("=" * 55)
