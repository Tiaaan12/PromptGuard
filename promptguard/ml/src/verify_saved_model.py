import json
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "promptguard_pipeline.joblib"
INFO_PATH = BASE_DIR / "model" / "model_information.json"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Saved model not found: {MODEL_PATH}")

pipeline = joblib.load(MODEL_PATH)

print("\n=== SAVED PIPELINE ===")
print("Path:", MODEL_PATH)


def inspect_pipeline(obj, name="pipeline"):
    print(f"\n{name}: {type(obj).__name__}")

    if isinstance(obj, Pipeline):
        for step_name, step in obj.steps:
            inspect_pipeline(step, f"{name}.{step_name}")

    elif isinstance(obj, FeatureUnion):
        for step_name, step in obj.transformer_list:
            inspect_pipeline(step, f"{name}.{step_name}")

    elif isinstance(obj, TfidfVectorizer):
        print("  Analyzer:", obj.analyzer)
        print("  N-gram range:", obj.ngram_range)

    elif isinstance(obj, LinearSVC):
        print("  C:", obj.C)
        print("  Class weight:", obj.class_weight)


inspect_pipeline(pipeline)

print("\n=== MODEL METADATA ===")
if INFO_PATH.exists():
    print(INFO_PATH.read_text(encoding="utf-8"))
else:
    print("model_information.json not found.")