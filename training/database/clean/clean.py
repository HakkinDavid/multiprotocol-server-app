import os
import sys
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = BASE_DIR
CLEAN_DIR = os.path.join(DB_DIR, "clean")

def clean_liga_mx(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    keep_cols = [
        "home_team", "away_team",
        "home_win", "away_win",
        "home_goals", "away_goals",
        "home_goals_half_time", "away_goals_half_time",
        "home_goals_fulltime", "away_goals_fulltime",
    ]

    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols].copy()

    score_cols = [
        "home_goals", "away_goals",
        "home_goals_half_time", "away_goals_half_time",
        "home_goals_fulltime", "away_goals_fulltime",
    ]

    for c in score_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    essential = [
        "home_team", "away_team",
        "home_goals_fulltime", "away_goals_fulltime",
        "home_goals_half_time", "away_goals_half_time",
    ]
    essential = [c for c in essential if c in df.columns]
    df = df.dropna(subset=essential)

    df = df.drop_duplicates()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

def build_paths(year: str):
    input_path = os.path.join(DB_DIR, f"2016-{year}_liga_mx.csv")
    output_path = os.path.join(CLEAN_DIR, f"2016-{year}_liga_mx_clean.csv")
    return input_path, output_path

if __name__ == "__main__":
    year = None
    if len(sys.argv) >= 2:
        year = sys.argv[1].strip()

    if year is None:
        year = "2024"

    input_path, output_path = build_paths(year)

    clean_liga_mx(input_path, output_path)
    print(output_path)