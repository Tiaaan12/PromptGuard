from pathlib import Path
from functools import lru_cache
import json

import joblib


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "model"
    / "promptguard_pipeline.joblib"
)

MODEL_INFO_PATH = (
    BASE_DIR
    / "model"
    / "model_information.json"
)


# ============================================================
# LOAD MODEL
# ============================================================

@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# ============================================================
# LOAD MODEL INFORMATION
# ============================================================

@lru_cache(maxsize=1)
def load_model_information():
    if not MODEL_INFO_PATH.exists():
        return {}

    with open(
        MODEL_INFO_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# PREDICT PROMPT
# ============================================================

def predict_prompt(prompt):
    if not isinstance(prompt, str):
        raise TypeError(
            "Prompt must be a string."
        )

    prompt = prompt.strip()

    if not prompt:
        raise ValueError(
            "Prompt cannot be empty."
        )

    model = load_model()

    prediction = int(
        model.predict([prompt])[0]
    )

    decision_score = float(
        model.decision_function([prompt])[0]
    )

    label = (
        "INJECTION"
        if prediction == 1
        else "BENIGN"
    )

    return {
        "prediction": label,
        "target": prediction,
        "decision_score": decision_score
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    prompt = str(input("Enter prompt: "))

    result = predict_prompt(prompt)

    print("\nPrompt:")
    print(prompt)

    print("\nPrediction:")
    print(result["prediction"])

    print("Target:")
    print(result["target"])

    print("Decision Score:")
    print(result["decision_score"])