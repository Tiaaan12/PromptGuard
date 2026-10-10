from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from data_preprocessing import load_dataset, preprocess_dataset, split_dataset
from augmentation import create_augmentation_v3, combine_training_data
from augment_and_finalize import get_final_pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "internal_dataset.csv"
RESULTS_PATH = BASE_DIR / "results" / "metrics"
ERRORS_PATH = BASE_DIR / "results" / "errors"

for directory in (RESULTS_PATH, ERRORS_PATH):
    directory.mkdir(parents=True, exist_ok=True)

def create_robustness_split():
    print("\nCreating fresh robustness validation split...")

    internal = preprocess_dataset(load_dataset(DATA_PATH))
    X_train, _, y_train, _ = split_dataset(internal)
    X_core, X_validation, y_core, y_validation = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=123,
        stratify=y_train,
    )

    X_core = X_core.reset_index(drop=True)
    y_core = y_core.reset_index(drop=True)
    X_validation = X_validation.reset_index(drop=True)
    y_validation = y_validation.reset_index(drop=True)

    print("\nOriginal training samples:", len(X_train))
    print("Core training samples:", len(X_core))
    print("Robustness validation samples:", len(X_validation))
    print("\nCore training distribution:")
    print(y_core.value_counts())
    print("\nValidation distribution:")
    print(y_validation.value_counts())

    return X_core, y_core, X_validation, y_validation


def save_prediction_errors(predictions_df, version_name):
    prefix = f"robustness_{version_name.lower()}"
    predictions_df.to_csv(ERRORS_PATH / f"{prefix}_predictions.csv", index=False)

    for file_suffix, error_type in (
        ("false_negatives", "false_negative"),
        ("false_positives", "false_positive"),
    ):
        predictions_df[predictions_df["error_type"] == error_type].to_csv(
            ERRORS_PATH / f"{prefix}_{file_suffix}.csv", index=False
        )
        
def evaluate_model(version_name, X_train, y_train, X_validation, y_validation):
    print(f"\nEvaluating {version_name}...")

    pipeline = get_final_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_validation)

    accuracy = accuracy_score(y_validation, predictions)
    precision = precision_score(y_validation, predictions, zero_division=0)
    recall = recall_score(y_validation, predictions, zero_division=0)
    f1 = f1_score(y_validation, predictions, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_validation, predictions).ravel()

    print(
        f"{version_name}: Accuracy={accuracy:.4f} | "
        f"Precision={precision:.4f} | Recall={recall:.4f} | "
        f"F1={f1:.4f} | FP={fp} | FN={fn}"
    )

    predictions_df = pd.DataFrame(
        {
            "text": X_validation.reset_index(drop=True),
            "actual": y_validation.reset_index(drop=True),
            "predicted": predictions,
            "decision_score": pipeline.decision_function(X_validation),
        }
    )
    predictions_df["error_type"] = "correct"
    predictions_df.loc[
        (predictions_df["actual"] == 0) & (predictions_df["predicted"] == 1),
        "error_type",
    ] = "false_positive"
    predictions_df.loc[
        (predictions_df["actual"] == 1) & (predictions_df["predicted"] == 0),
        "error_type",
    ] = "false_negative"
    save_prediction_errors(predictions_df, version_name)

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

def build_comparison(results):
    results_df = pd.DataFrame(results)
    baseline = results_df.loc[results_df["version"] == "Baseline"].iloc[0]
    results_df["f1_change_vs_baseline"] = results_df["f1"] - baseline["f1"]
    results_df["recall_change_vs_baseline"] = (
        results_df["recall"] - baseline["recall"]
    )
    results_df["fn_change_vs_baseline"] = (
        results_df["false_negatives"] - baseline["false_negatives"]
    )
    return results_df


def main():
    print("\n" + "=" * 70)
    print("PROMPTGUARD ROBUSTNESS VALIDATION")
    print("=" * 70)

    X_core, y_core, X_validation, y_validation = create_robustness_split()
    v3_data = create_augmentation_v3()

    print("\nV3 synthetic samples:", len(v3_data))
    print("\nV3 distribution:")
    print(v3_data["target"].value_counts())

    baseline_data = (X_core.copy(), y_core.copy())
    v3_X, v3_y = combine_training_data(X_core, y_core, v3_data)
    print("\nBaseline training samples:", len(baseline_data[0]))
    print("V3 training samples:", len(v3_X))

    results = [
        evaluate_model("Baseline", *baseline_data, X_validation, y_validation),
        evaluate_model("V3", v3_X, v3_y, X_validation, y_validation),
    ]
    results_df = build_comparison(results)

    output_path = RESULTS_PATH / "robustness_validation.csv"
    results_df.to_csv(output_path, index=False)

    print("\n" + "=" * 70)
    print("ROBUSTNESS VALIDATION RESULTS")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print("\nSaved:")
    print(output_path)
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
