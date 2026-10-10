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


def evaluate_version(version_name, X_train, y_train, X_external, y_external):
    print(f"\nEvaluating {version_name}...")

    pipeline = get_final_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_external)

    accuracy = accuracy_score(y_external, predictions)
    precision = precision_score(y_external, predictions, zero_division=0)
    recall = recall_score(y_external, predictions, zero_division=0)
    f1 = f1_score(y_external, predictions, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_external, predictions).ravel()

    print(
        f"{version_name}: "
        f"Accuracy={accuracy:.4f} | "
        f"Precision={precision:.4f} | "
        f"Recall={recall:.4f} | "
        f"F1={f1:.4f} | "
        f"FP={fp} | FN={fn}"
    )

    errors = pd.DataFrame(
        {
            "text": X_external.reset_index(drop=True),
            "actual": y_external.reset_index(drop=True),
            "predicted": pd.Series(predictions),
            "decision_score": pd.Series(
                pipeline.decision_function(X_external)
            ),
        }
    )
    errors["error_type"] = "correct"
    errors.loc[
        (errors["actual"] == 0) & (errors["predicted"] == 1),
        "error_type",
    ] = "false_positive"
    errors.loc[
        (errors["actual"] == 1) & (errors["predicted"] == 0),
        "error_type",
    ] = "false_negative"

    filename_prefix = f"external_{version_name.lower()}"
    errors.to_csv(ERRORS_PATH / f"{filename_prefix}_predictions.csv", index=False)
    errors[errors["error_type"] == "false_negative"].to_csv(
        ERRORS_PATH / f"{filename_prefix}_false_negatives.csv", index=False
    )
    errors[errors["error_type"] == "false_positive"].to_csv(
        ERRORS_PATH / f"{filename_prefix}_false_positives.csv", index=False
    )

    return {
        "version": version_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
    }


def build_training_versions(X_train, y_train):
    v1 = create_augmentation_v1()
    v2 = create_augmentation_v2()
    v3 = create_augmentation_v3()

    return {
        "Baseline": (X_train.reset_index(drop=True), y_train.reset_index(drop=True)),
        "V1": combine_training_data(X_train, y_train, v1),
        "V2": combine_training_data(X_train, y_train, v2),
        "V3": combine_training_data(X_train, y_train, v3),
    }


def main():
    print("\n" + "=" * 70)
    print("PROMPTGUARD EXTERNAL EVALUATION")
    print("=" * 70)

    internal = preprocess_dataset(load_dataset(INTERNAL_PATH))
    X_train, _, y_train, _ = split_dataset(internal)
    print("\nInternal training samples:", len(X_train))
    external = prepare_external_dataset(load_external_dataset())
    X_external = external["prompt"]
    y_external = external["target"]
    print("\nExternal TEST samples:", len(external))
    print("\nExternal TEST distribution:")
    print(y_external.value_counts())

    results = [
        evaluate_version(
            version_name,
            X_version,
            y_version,
            X_external,
            y_external,
        )
        for version_name, (X_version, y_version) in build_training_versions(
            X_train, y_train
        ).items()
    ]

    results_df = pd.DataFrame(results)
    baseline = results_df.loc[results_df["version"] == "Baseline"].iloc[0]
    results_df["f1_change_vs_baseline"] = results_df["f1"] - baseline["f1"]
    results_df["recall_change_vs_baseline"] = (
        results_df["recall"] - baseline["recall"]
    )
    results_df["fn_change_vs_baseline"] = (
        results_df["false_negatives"] - baseline["false_negatives"]
    )

    output_path = RESULTS_PATH / "external_evaluation.csv"
    results_df.to_csv(output_path, index=False)

    print("\n" + "=" * 70)
    print("EXTERNAL TEST EVALUATION RESULTS")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()

