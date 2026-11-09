"""Synthetic metabolic dataset generator for the Bio-Digital Twin project.

Produces 10 lifestyle/clinical features plus a simulated fasting glucose
target (mg/dL) and writes the result to
`ml_service/data/metabolic_data.csv`.
"""

from pathlib import Path

import numpy as np
import pandas as pd

_OUTPUT_CSV: Path = Path(__file__).resolve().parent / "data" / "metabolic_data.csv"
_RANDOM_SEED: int = 42

_AGE_MIN: int = 18
_AGE_MAX: int = 70
_BMI_MIN: float = 18.5
_BMI_MAX: float = 38.0
_SLEEP_MIN: float = 4.0
_SLEEP_MAX: float = 9.0
_ALCOHOL_MIN: float = 0.0
_ALCOHOL_MAX: float = 15.0
_YEARS_HABIT_MIN: int = 1
_YEARS_HABIT_MAX: int = 10
_STEPS_MIN: int = 2000
_STEPS_MAX: int = 15000
_CALORIE_MIN: float = 1500.0
_CALORIE_MAX: float = 3500.0
_SUGAR_MIN: float = 20.0
_SUGAR_MAX: float = 120.0
_STRESS_MIN: int = 1
_STRESS_MAX: int = 10
_SYSTOLIC_MIN: int = 100
_SYSTOLIC_MAX: int = 160
_NOISE_SD_MG_DL: float = 2.0
_GLUCOSE_FLOOR_MG_DL: float = 60.0
_GLUCOSE_CEIL_MG_DL: float = 300.0


class HealthDataGenerator:
    """Generate rows of simulated lifestyle features and glucose index."""

    def __init__(self, seed: int = _RANDOM_SEED) -> None:
        """Store the RNG seed so datasets are reproducible across runs.

        Args:
            seed: Seed for `numpy.random.default_rng`.
        """
        self.seed = seed

    @staticmethod
    def _glucose_formula(age: np.ndarray, bmi: np.ndarray, sleep_hours: np.ndarray,
                         alcohol_units: np.ndarray, years_habit: np.ndarray,
                         daily_steps: np.ndarray, caloric_intake: np.ndarray,
                         sugar_intake: np.ndarray, stress_level: np.ndarray,
                         systolic_bp: np.ndarray) -> np.ndarray:
        """Map the 10 feature columns to the simulated glucose index in mg/dL.

        Args:
            age: Age in years.
            bmi: Body mass index in kg/m^2.
            sleep_hours: Average nightly sleep in hours.
            alcohol_units: Weekly alcohol units.
            years_habit: Years of accumulated lifestyle, int 1-10.
            daily_steps: Walking activity per day, steps.
            caloric_intake: Daily energy intake, kcal.
            sugar_intake: Daily sugar intake, grams.
            stress_level: Perceived stress on a 1-10 scale.
            systolic_bp: Systolic blood pressure in mmHg.

        Returns:
            Glucose index per row, before observation noise:
            `80 + 0.2*age + 5*signed(bmi-22.5)^1.2 - 3*(sleep_hours-7)
            + 1.5*alcohol_units + 0.8*years_habit
            - 0.0015*(daily_steps-7500) + 0.004*(caloric_intake-2200)
            + 0.15*(sugar_intake-50) + 0.9*(stress_level-5)
            + 0.25*(systolic_bp-120)`. Fractional exponent 1.2 on negative
            bases (bmi < 22.5) is applied through `sign*|x|^1.2` so the term
            keeps its clinical direction instead of becoming NaN.
        """
        bmi_term = 5.0 * np.sign(bmi - 22.5) * np.abs(bmi - 22.5) ** 1.2
        return (
            80.0
            + 0.2 * age
            + bmi_term
            - 3.0 * (sleep_hours - 7.0)
            + 1.5 * alcohol_units
            + 0.8 * years_habit
            - 0.0015 * (daily_steps - 7500.0)
            + 0.004 * (caloric_intake - 2200.0)
            + 0.15 * (sugar_intake - 50.0)
            + 0.9 * (stress_level - 5.0)
            + 0.25 * (systolic_bp - 120.0)
        )

    def generate_dataset(self, n_samples: int = 600) -> pd.DataFrame:
        """Draw `n_samples` lifestyle rows and compute their glucose index.

        Args:
            n_samples: Number of rows to generate (600 satisfies the
                >= 500-row requirement).

        Returns:
            DataFrame with 11 columns: `age` (int, 18-70 years), `bmi`
            (float, 18.5-38.0 kg/m^2), `sleep_hours` (float, 4.0-9.0 h),
            `alcohol_units` (float, 0.0-15.0 units/week), `years_habit`
            (int, 1-10 years), `daily_steps` (int, 2000-15000 steps),
            `caloric_intake` (float, 1500-3500 kcal), `sugar_intake`
            (float, 20.0-120.0 g), `stress_level` (int, 1-10),
            `systolic_bp` (int, 100-160 mmHg) and target `glucose` (float,
            mg/dL, clipped to the physiological [60.0, 300.0] band after
            Gaussian noise with sd 2.0, rounded to 2 decimals).
        """
        rng = np.random.default_rng(self.seed)
        age = rng.integers(_AGE_MIN, _AGE_MAX + 1, n_samples)
        bmi = np.round(rng.uniform(_BMI_MIN, _BMI_MAX, n_samples), 2)
        sleep_hours = np.round(rng.uniform(_SLEEP_MIN, _SLEEP_MAX, n_samples), 2)
        alcohol_units = np.round(rng.uniform(_ALCOHOL_MIN, _ALCOHOL_MAX, n_samples), 2)
        years_habit = rng.integers(_YEARS_HABIT_MIN, _YEARS_HABIT_MAX + 1, n_samples)
        daily_steps = rng.integers(_STEPS_MIN, _STEPS_MAX + 1, n_samples)
        caloric_intake = np.round(rng.uniform(_CALORIE_MIN, _CALORIE_MAX, n_samples), 1)
        sugar_intake = np.round(rng.uniform(_SUGAR_MIN, _SUGAR_MAX, n_samples), 1)
        stress_level = rng.integers(_STRESS_MIN, _STRESS_MAX + 1, n_samples)
        systolic_bp = rng.integers(_SYSTOLIC_MIN, _SYSTOLIC_MAX + 1, n_samples)
        glucose = (
            self._glucose_formula(
                age.astype(float), bmi, sleep_hours, alcohol_units,
                years_habit.astype(float), daily_steps.astype(float),
                caloric_intake, sugar_intake, stress_level.astype(float),
                systolic_bp.astype(float),
            )
            + rng.normal(0.0, _NOISE_SD_MG_DL, n_samples)
        )
        # Counter-regulation keeps fasting glucose inside a survivable band,
        # so extreme lifestyle combinations saturate instead of diverging.
        glucose = np.clip(glucose, _GLUCOSE_FLOOR_MG_DL, _GLUCOSE_CEIL_MG_DL)
        return pd.DataFrame(
            {
                "age": age,
                "bmi": bmi,
                "sleep_hours": sleep_hours,
                "alcohol_units": alcohol_units,
                "years_habit": years_habit,
                "daily_steps": daily_steps,
                "caloric_intake": caloric_intake,
                "sugar_intake": sugar_intake,
                "stress_level": stress_level,
                "systolic_bp": systolic_bp,
                "glucose": np.round(glucose, 2),
            }
        )

    def save_dataset(self, df: pd.DataFrame, path: Path = _OUTPUT_CSV) -> Path:
        """Write the dataset to CSV, creating the parent directory if needed.

        Args:
            df: Dataset from `generate_dataset`.
            path: Destination file path.

        Returns:
            The absolute path written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", None)
    generator = HealthDataGenerator()
    df = generator.generate_dataset()
    saved_path = generator.save_dataset(df)
    print("df.shape =", df.shape)
    print(df.head())
    print("glucose min/max =", df["glucose"].min(), "/", df["glucose"].max())
    print("saved ->", saved_path)
