"""FastAPI glucose risk service for the Bio-Digital Twin project.

Serves the grid-searched artifacts from `ml_service/saved_models/`
(`best_svr.joblib` + `scaler.joblib`, trained by `trainer.py` on the 21
BRFSS 2015 risk indicators) behind POST /api/v1/predict-glucose.

Run with: .venv\\Scripts\\python.exe -m uvicorn ml_service.main_api:app
"""

from pathlib import Path

import numpy as np
from fastapi import FastAPI
from joblib import load
from pydantic import BaseModel, Field

_MODULE_DIR: Path = Path(__file__).resolve().parent

_svr = load(_MODULE_DIR / "saved_models" / "best_svr.joblib")
_scaler = load(_MODULE_DIR / "saved_models" / "scaler.joblib")

app = FastAPI(title="Bio-Digital Twin Glucose API")

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

_BINARY_CONSTRAINTS: dict[str, float] = {"ge": 0.0, "le": 1.0}
_SCORE_FLOOR: float = 0.0
_SCORE_CEIL: float = 2.0


class SimulationRequest(BaseModel):
    """The 21 BRFSS 2015 risk indicators of one respondent."""

    HighBP: float = Field(**_BINARY_CONSTRAINTS, description="High blood pressure flag")
    HighChol: float = Field(**_BINARY_CONSTRAINTS, description="High cholesterol flag")
    CholCheck: float = Field(**_BINARY_CONSTRAINTS, description="Cholesterol checked in last 5 years")
    BMI: float = Field(gt=0.0, description="Body mass index in kg/m^2")
    Smoker: float = Field(**_BINARY_CONSTRAINTS, description="Smoked at least 100 cigarettes")
    Stroke: float = Field(**_BINARY_CONSTRAINTS, description="History of stroke")
    HeartDiseaseorAttack: float = Field(**_BINARY_CONSTRAINTS, description="Heart disease or attack")
    PhysActivity: float = Field(**_BINARY_CONSTRAINTS, description="Physical activity in last 30 days")
    Fruits: float = Field(**_BINARY_CONSTRAINTS, description="Fruit at least once a day")
    Veggies: float = Field(**_BINARY_CONSTRAINTS, description="Vegetables at least once a day")
    HvyAlcoholConsump: float = Field(**_BINARY_CONSTRAINTS, description="Heavy alcohol consumption")
    AnyHealthcare: float = Field(**_BINARY_CONSTRAINTS, description="Has health coverage")
    NoDocbcCost: float = Field(**_BINARY_CONSTRAINTS, description="Skipped a doctor due to cost")
    GenHlth: float = Field(ge=1.0, le=5.0, description="Self-rated general health, 1-5 scale")
    MentHlth: float = Field(ge=0.0, le=30.0, description="Poor mental health days in last 30")
    PhysHlth: float = Field(ge=0.0, le=30.0, description="Poor physical health days in last 30")
    DiffWalk: float = Field(**_BINARY_CONSTRAINTS, description="Difficulty walking or climbing stairs")
    Sex: float = Field(**_BINARY_CONSTRAINTS, description="0.0 female, 1.0 male")
    Age: float = Field(ge=1.0, le=13.0, description="Age band, 1-13")
    Education: float = Field(ge=1.0, le=6.0, description="Education level, 1-6")
    Income: float = Field(ge=1.0, le=8.0, description="Income band, 1-8")


class SimulationResponse(BaseModel):
    """Predicted diabetes-risk score and its Vietnamese risk category."""

    predicted_score: float = Field(
        description="Predicted Diabetes_012 score on the [0.0, 2.0] scale, 2 decimals"
    )
    risk_level: str = Field(
        description="'Nguy cơ thấp' <0.5, 'Nguy cơ trung bình (Tiền tiểu đường)' "
        "0.5-1.4, 'Nguy cơ cao (Tiểu đường)' >=1.5"
    )


def classify_risk(score: float) -> str:
    """Map a predicted Diabetes_012 score to its risk category.

    Args:
        score: Predicted diabetes-risk score on the Diabetes_012 scale,
            where 0.0 is no diabetes, 1.0 prediabetes and 2.0 diabetes.

    Returns:
        'Nguy cơ thấp' below 0.5, 'Nguy cơ trung bình (Tiền tiểu đường)'
        from 0.5 up to 1.4, 'Nguy cơ cao (Tiểu đường)' at 1.5 and above.
    """
    if score < 0.5:
        return "Nguy cơ thấp"
    if score < 1.5:
        return "Nguy cơ trung bình (Tiền tiểu đường)"
    return "Nguy cơ cao (Tiểu đường)"


@app.post("/api/v1/predict-glucose", response_model=SimulationResponse)
def predict_glucose_endpoint(request: SimulationRequest) -> SimulationResponse:
    """Predict the diabetes-risk score for one respondent via the SVR model.

    Flow (per the service design diagram): validated request -> positional
    float array of shape (1, 21) -> `scaler.transform` -> `best_svr.predict`
    -> clip to the Diabetes_012 [0, 2] scale -> risk classification. SVR
    regression is unbounded, so without the clip a strong profile can return
    a score the target scale cannot express.

    Args:
        request: The 21 BRFSS indicators validated by `SimulationRequest`.

    Returns:
        `SimulationResponse` with the score rounded to 2 decimals and its
        `risk_level` category.
    """
    values = [getattr(request, column) for column in FEATURE_COLUMNS]
    input_array = np.asarray([values], dtype=float)
    raw_score = float(_svr.predict(_scaler.transform(input_array))[0])
    predicted_score = round(float(np.clip(raw_score, _SCORE_FLOOR, _SCORE_CEIL)), 2)
    return SimulationResponse(
        predicted_score=predicted_score,
        risk_level=classify_risk(predicted_score),
    )
