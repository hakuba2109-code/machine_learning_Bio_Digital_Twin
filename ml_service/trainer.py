"""Grid-search SVR trainer for the Bio-Digital Twin glucose model.

Reads the 21-column BRFSS 2015 sample (`diabetes_500_balanced.csv`), fits
StandardScaler + SVR(kernel 'rbf') through an 80/20 split, tunes C and gamma
with GridSearchCV, reports R2 and MAE on the held-out test set, and saves
`best_svr.joblib` plus `scaler.joblib` to `ml_service/saved_models/`.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn import clone

_MODULE_DIR: Path = Path(__file__).resolve().parent
_REPO_ROOT: Path = _MODULE_DIR.parent
_DATA_CSV: Path = (
    _REPO_ROOT
    / "diabetes_012_health_indicators_BRFSS2015.csv"
    / "diabetes_500_balanced.csv"
)
_SAVED_MODELS_DIR: Path = _MODULE_DIR / "saved_models"

FEATURE_COLUMNS: tuple[str, ...] = (
    "HighBP",
    "HighChol",
    "CholCheck",
    "BMI",
    "Smoker",
    "Stroke",
    "HeartDiseaseorAttack",
    "PhysActivity",
    "Fruits",
    "Veggies",
    "HvyAlcoholConsump",
    "AnyHealthcare",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Sex",
    "Age",
    "Education",
    "Income",
)
TARGET_COLUMN: str = "Diabetes_012"

_PARAMETER_GRID: dict[str, list[Any]] = {
    "svr__C": [0.1, 1, 10, 100],
    "svr__gamma": [0.001, 0.01, 0.1, 1.0],
    "svr__kernel": ["rbf"],
}

_TEST_SIZE: float = 0.2
_RANDOM_SEED: int = 42


def load_dataset(csv_path: Path = _DATA_CSV) -> tuple[np.ndarray, pd.Series]:
    """Read the BRFSS CSV and split it into features and target.

    Args:
        csv_path: Path to `metabolic_data.csv`.

    Returns:
        Tuple `(X, y)`: `X` is a float array of shape `(n, 21)` holding the
        BRFSS risk indicators in `FEATURE_COLUMNS` order (binary flags, BMI
        in kg/m^2, ordinal GenHlth 1-5, MentHlth/PhysHlth bad days 0-30,
        Sex, Age band 1-13, Education 1-6, Income 1-8); `y` is the
        `Diabetes_012` target Series (0.0 no diabetes, 1.0 prediabetes,
        2.0 diabetes). Fitting on a positional array keeps the saved scaler
        usable with raw numpy rows.
    """
    df = pd.read_csv(csv_path)
    X = df[list(FEATURE_COLUMNS)].to_numpy(float)
    y = df[TARGET_COLUMN]
    return X, y


def build_pipeline() -> Pipeline:
    """Build the scaled SVR pipeline tuned by GridSearchCV.

    Returns:
        Unfitted `StandardScaler` then `SVR(kernel='rbf')` pipeline; the
        scaler only ever fits on training folds, never on test rows.
    """
    return make_pipeline(StandardScaler(), SVR(kernel="rbf"))


def train_and_evaluate(
    csv_path: Path = _DATA_CSV,
) -> tuple[Pipeline, StandardScaler, dict[str, float]]:
    """Grid-search the best SVR and score it on the 20% held-out test set.

    Args:
        csv_path: BRFSS CSV consumed by `load_dataset`.

    Returns:
        Tuple `(best_svr, scaler, metrics)`: the tuned SVR (already fitted on
        the scaled 80% train split), that fitted `StandardScaler`, and a dict
        with `r2` (0-1, higher better) and `mae` (in Diabetes_012 score
        units, lower better), each rounded to 2 decimals.
    """
    X, y = load_dataset(csv_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=_TEST_SIZE, random_state=_RANDOM_SEED
    )

    search = GridSearchCV(
        estimator=build_pipeline(),
        param_grid=_PARAMETER_GRID,
        scoring="neg_mean_absolute_error",
    )
    search.fit(X_train, y_train)

    best_pipeline: Pipeline = search.best_estimator_
    scaler: StandardScaler = best_pipeline.named_steps["standardscaler"]
    best_svr: SVR = clone(best_pipeline.named_steps["svr"])
    X_train_scaled = scaler.transform(X_train)
    best_svr.fit(X_train_scaled, y_train)

    X_test_scaled = scaler.transform(X_test)
    y_pred = best_svr.predict(X_test_scaled)
    metrics = {
        "r2": round(float(r2_score(y_test, y_pred)), 2),
        "mae": round(float(mean_absolute_error(y_test, y_pred)), 2),
    }
    return best_svr, scaler, metrics


def save_models(
    best_svr: SVR, scaler: StandardScaler, out_dir: Path = _SAVED_MODELS_DIR
) -> tuple[Path, Path]:
    """Persist the tuned SVR and fitted scaler as joblib artifacts.

    Args:
        best_svr: The grid-searched SVR fitted on scaled training data.
        scaler: The `StandardScaler` fitted on the same training split.
        out_dir: Destination directory, created when missing.

    Returns:
        Paths of `best_svr.joblib` and `scaler.joblib`.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "best_svr.joblib"
    scaler_path = out_dir / "scaler.joblib"
    dump(best_svr, model_path)
    dump(scaler, scaler_path)
    return model_path, scaler_path


def main() -> None:
    """Train, evaluate, save artifacts and print the headline numbers."""
    X, _ = load_dataset()
    print(f"X.shape = {X.shape}  # rows x feature columns, target excluded")
    best_svr, scaler, metrics = train_and_evaluate()
    model_path, scaler_path = save_models(best_svr, scaler)
    print(f"kernel = {best_svr.kernel}")
    print(f"best C = {best_svr.C}")
    print(f"best gamma = {best_svr.gamma}")
    print(f"R2 score = {metrics['r2']}")
    print(f"MAE = {metrics['mae']} score units")
    print("saved ->", model_path, scaler_path)


if __name__ == "__main__":
    main()
