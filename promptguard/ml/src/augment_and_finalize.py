from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from augmentation import (
    combine_training_data,
    create_augmentation_v1,
    create_augmentation_v2,
    create_augmentation_v3,
)
from data_preprocessing import load_dataset, preprocess_dataset, split_dataset
from feature_pipeline import get_feature_configs


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "internal_dataset.csv"
AUGMENTED_PATH = BASE_DIR / "data" / "augmented"
MODEL_PATH = BASE_DIR / "model"
METRICS_PATH = BASE_DIR / "results" / "metrics"
ERRORS_PATH = BASE_DIR / "results" / "errors"
SELECTED_VERSION = "V3"

for path in (AUGMENTED_PATH, MODEL_PATH, METRICS_PATH, ERRORS_PATH):
    path.mkdir(parents=True, exist_ok=True)


def get_final_pipeline():
    return Pipeline([
        ("features", get_feature_configs()["Char_3_5"]),
        ("model", LinearSVC(C=1, class_weight="balanced", random_state=42)),
    ])
