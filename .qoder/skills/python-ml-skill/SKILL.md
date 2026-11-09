---
name: python-ml-skill
description: Python coding standards for the Bio-Digital Twin project. Apply when writing, editing, or reviewing any Python code in this repository, especially scikit-learn SVR/machine-learning scripts, feature pipelines, and prediction utilities. Enforces type hints, docstrings on every function, StandardScaler before SVR prediction, and rounding of float results to 2 decimals.
---

# Python ML standards — Bio-Digital Twin

## Overview

Every Python file in this project must follow four mandatory rules below. They
exist because SVR with an RBF kernel is scale-sensitive, and because numeric
outputs feed a digital-twin UI that expects stable, display-ready values.

## Mandatory rules

### 1. Type hints on every function

All parameters and return values must be annotated. Use `typing` only where
built-ins cannot express the type (`list[list[float]]`, `np.ndarray`, unions).

```python
def predict(age: int, gamma: float = 0.002) -> float: ...
```

### 2. Docstring on every function

One-line imperative summary, plus `Args:`/`Returns:` when parameters are not
obvious. Document units (years, score, ms) since survey features mix scales.

### 3. StandardScaler before SVR prediction

Always scale features with `sklearn.preprocessing.StandardScaler` and pass the
scaled values to `SVR`. Fit the scaler on training data **only**, then transform
train and new inputs with the same fitted object — never fit on the prediction
input (data leakage).

Use a `Pipeline` by default; it makes the fit-only-on-train rule impossible to
break:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

model = make_pipeline(SVR(kernel="rbf", C=10, gamma=0.002))
```

Note: scaling changes predictions versus raw features. On the survey sample
`X=[[30],[50],[70],[100]]`, `y=[6.0,9.0,11.0,15.0]`, `x_new=[[55]]` with
`C=10, gamma=0.002`: unscaled SVR returns ~9.64, scaled pipeline returns
~9.97. Re-baseline any expected numbers after adding the scaler.

### 4. Round returned floats to 2 decimals

Every `float` a function returns must be rounded with `round(value, 2)`. Apply
it at the return boundary only — never round intermediate math, arrays, or
model internals.

```python
return round(float(y_pred[0]), 2)
```

## Canonical example

```python
"""SVR demo for the Bio-Digital Twin survey model."""

from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


def build_model() -> Pipeline:
    """Build the scaled SVR regressant used by the survey feature.

    Returns:
        An unfitted pipeline: StandardScaler then SVR(kernel='rbf').
    """
    return make_pipeline(StandardScaler(), SVR(kernel="rbf", C=10, gamma=0.002))


def predict_score(x_train: list[list[float]], y_train: list[float], x_new: list[list[float]]) -> float:
    """Fit the SVR model and predict the target for a single input row.

    Args:
        x_train: Training feature rows, each `[age_in_years]`.
        y_train: Survey scores matching `x_train`.
        x_new: One feature row to predict, e.g. `[[55]]`.

    Returns:
        Predicted score rounded to 2 decimals.
    """
    model = build_model().fit(x_train, y_train)
    return round(float(model.predict(x_new)[0]), 2)


if __name__ == "__main__":
    X = [[30], [50], [70], [100]]
    y = [6.0, 9.0, 11.0, 15.0]
    print("y_pred =", predict_score(X, y, [[55]]))
```

## Running code

Use the project virtualenv, not global Python (global site-packages also has
scikit-learn and will mask a broken `.venv`):

```
D:\DOAN\Do_An_Bio_Digital_Twin\.venv\Scripts\python.exe test_svr_demo.py
```

Dependencies live in `requirements.txt`; install with
`.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Pre-commit checklist

- [ ] Every `def` has parameter and return annotations.
- [ ] Every `def` has a docstring.
- [ ] SVR is wrapped in a scaler (`StandardScaler` or a `Pipeline`).
- [ ] `round(value, 2)` on each returned float.
- [ ] Script runs with the `.venv` interpreter, no traceback.

Quick audit of the repo:

```
grep -rn "def " --include=*.py . | grep -v "->" 
grep -rn "SVR(" --include=*.py .
```

The first command lists functions missing return hints; the second confirms
each SVR site has a scaler nearby.
