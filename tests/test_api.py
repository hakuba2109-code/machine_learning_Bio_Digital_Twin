"""Pytest suite for the FastAPI glucose endpoint using TestClient.

Covers main_api.py with the 21 BRFSS indicators: full-payload prediction and
JSON shape, the three Vietnamese risk bands, and 422 rejection of payloads
outside the documented ranges.
"""

import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml_service.main_api import app

_CLIENT = TestClient(app)
_ENDPOINT = "/api/v1/predict-glucose"

RISK_LEVELS: tuple[str, ...] = (
    "Nguy cơ thấp",
    "Nguy cơ trung bình (Tiền tiểu đường)",
    "Nguy cơ cao (Tiểu đường)",
)


def _payload(**overrides: Any) -> dict[str, Any]:
    """Build a valid 21-field request body, overriding only given fields.

    Args:
        overrides: Field name to new value, e.g. `BMI=40.0`.

    Returns:
        Mutable dict ready to POST, holding one high-risk BRFSS respondent.
    """
    body: dict[str, Any] = {
        "HighBP": 1.0,
        "HighChol": 1.0,
        "CholCheck": 1.0,
        "BMI": 28.0,
        "Smoker": 1.0,
        "Stroke": 0.0,
        "HeartDiseaseorAttack": 1.0,
        "PhysActivity": 0.0,
        "Fruits": 0.0,
        "Veggies": 0.0,
        "HvyAlcoholConsump": 0.0,
        "AnyHealthcare": 1.0,
        "NoDocbcCost": 0.0,
        "GenHlth": 4.0,
        "MentHlth": 10.0,
        "PhysHlth": 15.0,
        "DiffWalk": 1.0,
        "Sex": 1.0,
        "Age": 9.0,
        "Education": 3.0,
        "Income": 2.0,
    }
    body.update(overrides)
    return body


def test_predict_glucose_returns_score_and_risk() -> None:
    """Full 21-field payload gets 200 and the documented JSON shape.

    Expect:
        Exactly `predicted_score` and `risk_level`; the score is a `float`
        inside the Diabetes_012 [0.0, 2.0] band at 2 decimals, and
        `risk_level` is one of the three Vietnamese categories.
    """
    response = _CLIENT.post(_ENDPOINT, json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"predicted_score", "risk_level"}
    score = body["predicted_score"]
    assert isinstance(score, float)
    assert 0.0 <= score <= 2.0
    assert score == round(score, 2)
    assert body["risk_level"] in RISK_LEVELS


@pytest.mark.parametrize(
    ("overrides", "expected_risk"),
    [
        (
            {
                "HighBP": 0.0,
                "HighChol": 0.0,
                "BMI": 21.0,
                "Smoker": 0.0,
                "HeartDiseaseorAttack": 0.0,
                "PhysActivity": 1.0,
                "Fruits": 1.0,
                "Veggies": 1.0,
                "GenHlth": 1.0,
                "MentHlth": 0.0,
                "PhysHlth": 0.0,
                "DiffWalk": 0.0,
                "Age": 3.0,
            },
            RISK_LEVELS[0],
        ),
        (
            {
                "HighBP": 1.0,
                "HighChol": 0.0,
                "BMI": 26.0,
                "Smoker": 0.0,
                "HeartDiseaseorAttack": 0.0,
                "PhysActivity": 1.0,
                "GenHlth": 3.0,
                "MentHlth": 5.0,
                "PhysHlth": 5.0,
                "DiffWalk": 0.0,
                "Age": 7.0,
            },
            RISK_LEVELS[1],
        ),
        (
            {
                "GenHlth": 5.0,
                "MentHlth": 25.0,
                "PhysHlth": 28.0,
                "BMI": 38.0,
                "Stroke": 1.0,
                "Age": 13.0,
            },
            RISK_LEVELS[2],
        ),
    ],
)
def test_risk_level_classification(overrides: dict[str, Any], expected_risk: str) -> None:
    """Check the response risk band agrees with the score thresholds.

    Args:
        overrides: Payload fields steering the prediction into a band.
        expected_risk: Band the returned `predicted_score` must fall in.
    """
    body = _CLIENT.post(_ENDPOINT, json=_payload(**overrides)).json()
    score = body["predicted_score"]
    if score < 0.5:
        band = RISK_LEVELS[0]
    elif score < 1.5:
        band = RISK_LEVELS[1]
    else:
        band = RISK_LEVELS[2]
    assert body["risk_level"] == band == expected_risk


@pytest.mark.parametrize(
    "overrides",
    [
        {"BMI": 0.0},
        {"BMI": -1.0},
        {"HighBP": 2.0},
        {"GenHlth": 0.0},
        {"GenHlth": 6.0},
        {"MentHlth": 31.0},
        {"Age": 14.0},
        {"Education": 0.0},
        {"Income": 9.0},
    ],
)
def test_invalid_payload_rejected(overrides: dict[str, Any]) -> None:
    """Out-of-range indicators must fail validation with 422.

    Args:
        overrides: A single out-of-range field per case.
    """
    response = _CLIENT.post(_ENDPOINT, json=_payload(**overrides))
    assert response.status_code == 422
