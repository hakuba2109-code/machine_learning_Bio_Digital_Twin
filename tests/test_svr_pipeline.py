"""Pytest suite for the SPEC_SVR glucose prediction pipeline.

Covers SPEC_SVR.md sections 3 and 5: valid-input prediction range, ValueError
on invalid parameters, and 2-decimal rounding of the output.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml_service.svr_pipeline import GlucosePredictor

predict_glucose = GlucosePredictor.predict_glucose

_VALID_ROW: np.ndarray = np.array([25, 22.5, 7.0, 1.0, 5], dtype=float)
_INVALID_NEGATIVE_ROW: np.ndarray = np.array([25, -5.0, 7.0, 1.0, 5], dtype=float)


def test_normal_prediction() -> None:
    """Predict for a valid row and check float type within [60.0, 300.0].

    Given:
        SPEC_SVR.md §2/§5: a valid input row [25, 22.5, 7.0, 1.0, 5].

    Expect:
        Scalar glucose value of type `float`, 60.0 <= value <= 300.0 mg/dL.
    """
    result = predict_glucose(_VALID_ROW)
    glucose = float(result[0])
    assert isinstance(glucose, float)
    assert 60.0 <= glucose <= 300.0


def test_invalid_input_raising_error() -> None:
    """Reject a negative BMI row with the exact SPEC_SVR ValueError message.

    Given:
        SPEC_SVR.md §3: input [25, -5.0, 7.0, 1.0, 5] violates bmi < 10.

    Expect:
        ValueError with message "Tham số đầu vào không hợp lệ".
    """
    with pytest.raises(ValueError, match="Tham số đầu vào không hợp lệ"):
        predict_glucose(_INVALID_NEGATIVE_ROW)


def test_output_rounded_two_decimals() -> None:
    """Check every returned glucose value keeps at most 2 decimal places.

    Given:
        SPEC_SVR.md §5: outputs are rounded to 2 decimals at the return
        boundary. Tested on one row and on a multi-row batch.

    Expect:
        Each value equals itself rounded to 2 decimals (exact for these
        magnitudes in IEEE double), so no extra digits leak out.
    """
    results = [
        predict_glucose(_VALID_ROW),
        predict_glucose(np.vstack([_VALID_ROW, [45.0, 27.0, 6.5, 8.0, 10.0]])),
    ]
    for batch in results:
        for value in np.atleast_1d(batch):
            assert float(value) == round(float(value), 2)
