"""NumPy prediction entrypoint for the Bio-Digital Twin glucose model.

Thin wrapper over `GlucosePredictor.predict_glucose` in `svr_pipeline.py`,
kept for the existing module-level import path.
"""

import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml_service.svr_pipeline import GlucosePredictor


def predict_glucose(X_input: np.ndarray) -> np.ndarray:
    """Predict the fasting glucose index (mg/dL) for lifestyle feature rows.

    Args:
        X_input: Array of shape `(n, 5)` or a single row of shape `(5,)`,
            columns in `FEATURE_NAMES` order: age (years), bmi (kg/m^2),
            sleep_hours (h/night), alcohol_units (units/week), years.

    Returns:
        Array of predicted glucose indices in mg/dL, clipped to
        [60.0, 300.0] and rounded to 2 decimals; shape `(n,)`.

    Raises:
        ValueError: See SPEC_SVR.md §3 for the input constraints.
    """
    return GlucosePredictor.predict_glucose(X_input)


if __name__ == "__main__":
    demo = np.array([[45.0, 27.0, 6.5, 8.0, 10.0]])
    print("glucose_index_mg_dl =", predict_glucose(demo))
