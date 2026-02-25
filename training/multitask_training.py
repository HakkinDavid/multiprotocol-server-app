import os
from typing import Tuple

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, f1_score, classification_report


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
CLEAN_DIR = os.path.join(DB_DIR, "clean")
MODEL_DIR = os.path.join(BASE_DIR, "models")

PATH_TRAIN = os.path.join(CLEAN_DIR, "2016-2024_liga_mx_clean.csv")


def load_and_prepare(path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)

    # keep relevant columns if present
    keep_cols = [
        "home_team", "away_team",
        "home_goals_half_time", "away_goals_half_time",
        "home_goals_fulltime", "away_goals_fulltime",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols].copy()

    # convert score columns to numeric
    score_cols = ["home_goals_half_time", "away_goals_half_time", "home_goals_fulltime", "away_goals_fulltime"]
    for c in score_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop rows missing teams or final scores
    df = df.dropna(subset=["home_team", "away_team", "home_goals_fulltime", "away_goals_fulltime"])

    # derive result
    df["result"] = np.where(
        df["home_goals_fulltime"] > df["away_goals_fulltime"], "H",
        np.where(df["home_goals_fulltime"] < df["away_goals_fulltime"], "A", "D")
    )

    features = ["home_team", "away_team", "home_goals_half_time", "away_goals_half_time"]
    df = df.dropna(subset=features)

    X = df[features].copy()
    y_goals = df[["home_goals_fulltime", "away_goals_fulltime"]].copy()
    y_result = df["result"].copy()

    return X, y_goals, y_result


def goals_to_result(pred_goals: np.ndarray) -> np.ndarray:
    # pred_goals is Nx2 array (home, away) possibly floats
    preds_rounded = np.rint(pred_goals).astype(int)
    preds_rounded = np.clip(preds_rounded, 0, None)
    res = []
    for h, a in preds_rounded:
        if h > a:
            res.append("H")
        elif h < a:
            res.append("A")
        else:
            res.append("D")
    return np.array(res)


def main():
    X, y_goals, y_result = load_and_prepare(PATH_TRAIN)
    print("Loaded dataset:", X.shape)

    X_train, X_test, y_goals_train, y_goals_test, y_result_train, y_result_test = train_test_split(
        X, y_goals, y_result, test_size=0.2, random_state=42, stratify=y_result
    )

    cat_features = ["home_team", "away_team"]
    num_features = ["home_goals_half_time", "away_goals_half_time"]

    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
            ("num", Pipeline([("scaler", StandardScaler())]), num_features),
        ],
        remainder="drop",
    )

    # Multi-output regressor to predict both final goals
    base_reg = RandomForestRegressor(random_state=42)
    multi_reg = MultiOutputRegressor(base_reg)

    pipe = Pipeline([
        ("preprocess", preprocess),
        ("model", multi_reg),
    ])

    param_grid = {
        "model__estimator__n_estimators": [100, 200],
        "model__estimator__max_depth": [None, 10],
        "model__estimator__min_samples_split": [2, 5],
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    grid = GridSearchCV(
        pipe,
        param_grid=param_grid,
        scoring="neg_mean_absolute_error",
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=True,
    )

    print("Fitting multi-output regressor (predicting final goals)...")
    grid.fit(X_train, y_goals_train)
    print("Best params:", grid.best_params_)
    print("Best CV score (neg MAE):", grid.best_score_)

    best = grid.best_estimator_

    # Predict goals on test
    y_pred_goals = best.predict(X_test)
    mae_home = mean_absolute_error(y_goals_test.iloc[:, 0], y_pred_goals[:, 0])
    mae_away = mean_absolute_error(y_goals_test.iloc[:, 1], y_pred_goals[:, 1])
    mse_home = mean_squared_error(y_goals_test.iloc[:, 0], y_pred_goals[:, 0])
    mse_away = mean_squared_error(y_goals_test.iloc[:, 1], y_pred_goals[:, 1])

    print(f"Test MAE - home: {mae_home:.4f}, away: {mae_away:.4f}")
    print(f"Test MSE - home: {mse_home:.4f}, away: {mse_away:.4f}")

    # Derive result from predicted goals and evaluate classification metrics
    y_pred_result = goals_to_result(y_pred_goals)

    acc = accuracy_score(y_result_test, y_pred_result)
    f1m = f1_score(y_result_test, y_pred_result, average="macro")

    print(f"Derived result - Accuracy: {acc:.4f}, F1-macro: {f1m:.4f}")
    print("Classification report for derived result:\n", classification_report(y_result_test, y_pred_result, digits=4))

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "best_model_multioutput_regressor.joblib")
    joblib.dump(best, model_path)
    print("Saved multi-output model to:", model_path)


if __name__ == "__main__":
    main()
