"""SVR glucose prediction pipeline for the Bio-Digital Twin project.

Implements SPEC_SVR.md: `GlucosePredictor.predict_glucose()` validates the
input rows, predicts with a StandardScaler + SVR(kernel='rbf') pipeline that
is fitted on the synthetic training set only, and returns values clipped to
[60.0, 300.0] mg/dL rounded to 2 decimals.
"""

import sys
from pathlib import Path

import numpy as np
from sklearn.pipeline import Pipeline

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from svr_service import FEATURE_NAMES, GlucosePredictor as _Trainer

_FEATURE_COUNT: int = len(FEATURE_NAMES)
_BMI_MIN: float = 10.0
_GLUCOSE_FLOOR_MG_DL: float = 60.0
_GLUCOSE_CEIL_MG_DL: float = 300.0


class GlucosePredictor:
    """Scaled SVR predictor of the fasting glucose index (mg/dL)."""

    _model: Pipeline | None = None

    @classmethod
    def _get_model(cls) -> Pipeline:
        """Return the fitted StandardScaler + SVR pipeline, training it once.

        Returns:
            Pipeline cached on the class; the scaler is fitted on the 600-row
            synthetic training set only, never on prediction input.
        """
        if cls._model is None:
            trainer = _Trainer(age=0, bmi=0.0, sleep_hours=0.0, alcohol_units=0.0, years=0)
            x_train, y_train = trainer._build_training_set()
            cls._model = trainer.build_model().fit(x_train, y_train)
        return cls._model

    @staticmethod
    def _as_feature_matrix(X_input: np.ndarray) -> np.ndarray:
        """Convert the input to a float matrix of shape `(n, 5)`.

        Args:
            X_input: Array of shape `(n, 5)` or a single row of shape `(5,)`,
                columns in `FEATURE_NAMES` order: age (years), bmi (kg/m^2),
                sleep_hours (h/night), alcohol_units (units/week), years.

        Returns:
            The input as a 2D float array.

        Raises:
            ValueError: If the array is not numeric-compatible or its shape
                is not `(n, 5)` / `(5,)`.
        """
        try:
            X = np.asarray(X_input, dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError("Tham số đầu vào không hợp lệ") from exc
        if X.ndim == 1:
            X = X.reshape(1, -1)
        if X.ndim != 2 or X.shape[1] != _FEATURE_COUNT:
            raise ValueError(
                f"X_input must have shape (n, {_FEATURE_COUNT}) "
                f"[{', '.join(FEATURE_NAMES)}], got {np.asarray(X_input).shape}"
            )
        return X

    @staticmethod
    def _validate_features(X: np.ndarray) -> None:
        """Check every row against the SPEC_SVR parameter constraints.

        Args:
            X: Array of shape `(n, 5)` in `FEATURE_NAMES` column order.

        Raises:
            ValueError: If any row has bmi < 10, sleep_hours < 0 or
                years < 0, with the exact SPEC_SVR.md §3 message.
        """
        bmi, sleep_hours, years = X[:, 1], X[:, 2], X[:, 4]
        if np.any(bmi < _BMI_MIN) or np.any(sleep_hours < 0.0) or np.any(years < 0.0):
            raise ValueError("Tham số đầu vào không hợp lệ")

    @staticmethod
    def predict_glucose(X_input: np.ndarray) -> np.ndarray:
        """Predict the fasting glucose index (mg/dL) for lifestyle rows.

        Args:
            X_input: Array of shape `(n, 5)` or one row of shape `(5,)`:
                [age (years), bmi (kg/m^2), sleep_hours (h/night),
                alcohol_units (units/week), years].

        Returns:
            Array of glucose indices in mg/dL, clipped to [60.0, 300.0] and
            rounded to 2 decimals; shape `(n,)`.

        Raises:
            ValueError: Invalid shape, or the exact message
                "Tham số đầu vào không hợp lệ" when any row has bmi < 10,
                sleep_hours < 0 or years < 0 (SPEC_SVR.md §3).
        """
        X = GlucosePredictor._as_feature_matrix(X_input)
        GlucosePredictor._validate_features(X)
        preds = GlucosePredictor._get_model().predict(X)
        clipped = np.clip(
            np.asarray(preds, dtype=float), _GLUCOSE_FLOOR_MG_DL, _GLUCOSE_CEIL_MG_DL
        )
        return np.round(clipped, 2)


if __name__ == "__main__":
    demo = np.array([[45, 27.0, 6.5, 8.0, 10]])
    print("features =", dict(zip(FEATURE_NAMES, demo[0])))
    print("glucose_index_mg_dl =", GlucosePredictor.predict_glucose(demo))
