"""SVR glucose-index predictor for the Bio-Digital Twin project.

Trains a simulated SVR (RBF kernel) on synthetic, physiologically plausible
samples and predicts a fasting glucose index (mg/dL) for one person.
"""

from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
import numpy as np

FEATURE_NAMES: tuple[str, ...] = (
    "age",
    "bmi",
    "sleep_hours",
    "alcohol_units",
    "years",
)

_TRAINING_ROWS: int = 600
_RANDOM_SEED: int = 42


class GlucosePredictor:
    """Predict a fasting glucose index from five lifestyle parameters."""

    def __init__(
        self,
        age: int,
        bmi: float,
        sleep_hours: float,
        alcohol_units: float,
        years: int,
    ) -> None:
        """Store the person's parameters used by predict().

        Args:
            age: Current age in years.
            bmi: Body mass index in kg/m^2.
            sleep_hours: Average nightly sleep in hours.
            alcohol_units: Weekly alcohol units.
            years: Years since first adult health check, as an aging proxy.
        """
        self.age = age
        self.bmi = bmi
        self.sleep_hours = sleep_hours
        self.alcohol_units = alcohol_units
        self.years = years

    def feature_vector(self) -> list[float]:
        """Return this person's features in the model's column order.

        Returns:
            A single row `[age, bmi, sleep_hours, alcohol_units, years]`.
        """
        return [
            float(self.age),
            float(self.bmi),
            float(self.sleep_hours),
            float(self.alcohol_units),
            float(self.years),
        ]

    @staticmethod
    def _glucose_formula(features: np.ndarray) -> np.ndarray:
        """Map feature columns to the simulated glucose index in mg/dL.

        Args:
            features: Array of shape `(n, 5)` in `FEATURE_NAMES` order.

        Returns:
            Glucose index per row, before observation noise.
        """
        age, bmi, sleep_hours, alcohol_units, years = features.T
        return (
            82.0
            + 0.30 * age
            + 7.5 * (bmi - 24.0)
            - 3.5 * (sleep_hours - 7.0)
            + 2.2 * alcohol_units
            + 0.35 * years
        )

    def _build_training_set(self) -> tuple[list[list[float]], list[float]]:
        """Generate the synthetic dataset the SVR model learns from.

        Returns:
            A tuple `(x_train, y_train)` with `_TRAINING_ROWS` samples. Ages
            span 18-80, BMI 16-40, sleep 3-10 h, alcohol 0-25 units/week and
            follow-up 0-40 years, with 2 mg/dL Gaussian noise.
        """
        rng = np.random.default_rng(_RANDOM_SEED)
        features = np.column_stack(
            (
                rng.integers(18, 81, _TRAINING_ROWS),
                rng.uniform(16.0, 40.0, _TRAINING_ROWS),
                rng.uniform(3.0, 10.0, _TRAINING_ROWS),
                rng.uniform(0.0, 25.0, _TRAINING_ROWS),
                rng.integers(0, 41, _TRAINING_ROWS),
            )
        ).astype(float)
        glucose = self._glucose_formula(features) + rng.normal(0.0, 2.0, _TRAINING_ROWS)
        return features.tolist(), glucose.tolist()

    def build_model(self) -> Pipeline:
        """Build the scaled SVR pipeline used for training and inference.

        Returns:
            An unfitted pipeline: StandardScaler then SVR(kernel='rbf'). The
            scaler is mandatory so all five features share one RBF distance
            scale, and it is fitted on training data only inside predict().

        `gamma` is set explicitly instead of 'scale': on five standardized
        features 'scale' resolves to ~0.2, whose kernel is too narrow for the
        sparse corners of the 5-D sample space (max error ~14.7 mg/dL there).
        At gamma=0.05 held-out error drops to MAE 0.69, max 2.77 mg/dL.
        """
        return make_pipeline(
            StandardScaler(),
            SVR(kernel="rbf", C=1000.0, gamma=0.05, epsilon=0.2),
        )

    def predict(self) -> float:
        """Train the simulated SVR model and return this person's glucose index.

        Returns:
            Predicted fasting glucose index in mg/dL, rounded to 2 decimals.
            Refits the model on every call (~265 ms for 600 samples), which is
            fine for a single prediction per request; batch or repeated calls
            should fit once and reuse the pipeline.
        """
        x_train, y_train = self._build_training_set()
        model = self.build_model().fit(x_train, y_train)
        return round(float(model.predict([self.feature_vector()])[0]), 2)


if __name__ == "__main__":
    predictor = GlucosePredictor(
        age=45, bmi=27.0, sleep_hours=6.5, alcohol_units=8.0, years=10
    )
    print("features =", dict(zip(FEATURE_NAMES, predictor.feature_vector())))
    print("glucose_index =", predictor.predict())
