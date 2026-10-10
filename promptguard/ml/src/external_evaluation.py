from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from data_preprocessing import load_dataset, preprocess_dataset, split_dataset
from augmentation import (
    create_augmentation_v1,
    create_augmentation_v2,
    create_augmentation_v3,
    combine_training_data,
)
from augment_and_finalize import get_final_pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
INTERNAL_PATH = BASE_DIR / "data" / "raw" / "internal_dataset.csv"
EXTERNAL_PATH = BASE_DIR / "data" / "external" / "external_dataset.csv"
RESULTS_PATH = BASE_DIR / "results" / "metrics"
ERRORS_PATH = BASE_DIR / "results" / "errors"

RESULTS_PATH.mkdir(parents=True, exist_ok=True)
ERRORS_PATH.mkdir(parents=True, exist_ok=True)


def load_external_dataset():
    external = pd.read_csv(EXTERNAL_PATH)
    print("\nExternal columns:")
    print(external.columns.tolist())
    print("\nExternal shape:")
    print(external.shape)
    print("\nExternal split distribution:")
    print(external["split"].value_counts())
    return external


def prepare_external_dataset(external):
    external = external[
        external["split"].astype(str).str.lower() == "test"
    ].copy()
    external = external[["prompt", "label"]].copy()
    external["prompt"] = external["prompt"].astype(str).str.strip()
    external = external.dropna(subset=["prompt", "label"])
    external["target"] = external["label"].map(
        {"benign": 0, "malicious": 1}
    )
    external = external.dropna(subset=["target"])
    external["target"] = external["target"].astype(int)
    return external

