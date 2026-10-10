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

def evaluate_cv(X, y, version):
    scores = cross_validate(
        get_final_pipeline(),
        X,
        y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring={
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
        },
        n_jobs=-1,
    )

    result = {"version": version, "training_samples": len(X)}
    for metric in ("accuracy", "precision", "recall", "f1"):
        result[f"{metric}_mean"] = scores[f"test_{metric}"].mean()
        result[f"{metric}_std"] = scores[f"test_{metric}"].std()
    return result

def save_test_artifacts(predictions, y_test, y_pred, version):
    prefix = version.lower()
    predictions.to_csv(ERRORS_PATH / f"{prefix}_predictions.csv", index=False)
    predictions[predictions["error_type"] == "false_negative"].to_csv(
        ERRORS_PATH / f"{prefix}_false_negatives.csv", index=False
    )
    predictions[predictions["error_type"] == "false_positive"].to_csv(
        ERRORS_PATH / f"{prefix}_false_positives.csv", index=False
    )

    pd.DataFrame(
        confusion_matrix(y_test, y_pred),
        index=["actual_benign", "actual_injection"],
        columns=["predicted_benign", "predicted_injection"],
    ).to_csv(METRICS_PATH / f"{prefix}_confusion_matrix.csv")

    report = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["benign", "injection"],
        output_dict=True,
        zero_division=0,
    )
    pd.DataFrame(report).transpose().to_csv(
        METRICS_PATH / f"{prefix}_classification_report.csv"
    )

def evaluate_test(X_train, y_train, X_test, y_test, version):
    pipeline = get_final_pipeline().fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    decision_scores = pipeline.decision_function(X_test)

    predictions = pd.DataFrame({
        "text": X_test.reset_index(drop=True),
        "actual": y_test.reset_index(drop=True),
        "predicted": pd.Series(y_pred),
        "decision_score": pd.Series(decision_scores),
    })
    predictions["error_type"] = "correct"
    predictions.loc[
        (predictions["actual"] == 0) & (predictions["predicted"] == 1),
        "error_type",
    ] = "false_positive"
    predictions.loc[
        (predictions["actual"] == 1) & (predictions["predicted"] == 0),
        "error_type",
    ] = "false_negative"
    save_test_artifacts(predictions, y_test, y_pred, version)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    return {
        "version": version,
        "test_accuracy": accuracy_score(y_test, y_pred),
        "test_precision": precision_score(y_test, y_pred, zero_division=0),
        "test_recall": recall_score(y_test, y_pred, zero_division=0),
        "test_f1": f1_score(y_test, y_pred, zero_division=0),
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
    }

def create_training_versions(X_train, y_train):
    augmentations = {
        "V1": create_augmentation_v1(),
        "V2": create_augmentation_v2(),
        "V3": create_augmentation_v3(),
    }
    for name, data in augmentations.items():
        data.to_csv(AUGMENTED_PATH / f"augmentation_{name.lower()}.csv", index=False)

    versions = {
        "Baseline": (X_train.reset_index(drop=True), y_train.reset_index(drop=True))
    }
    versions.update({
        name: combine_training_data(X_train, y_train, data)
        for name, data in augmentations.items()
    })
    return augmentations, versions

def save_final_model(X_train, y_train, X_test, y_test, selected_cv):
    pipeline = get_final_pipeline().fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()

    metrics = {
        "test_accuracy": accuracy_score(y_test, predictions),
        "test_precision": precision_score(y_test, predictions, zero_division=0),
        "test_recall": recall_score(y_test, predictions, zero_division=0),
        "test_f1": f1_score(y_test, predictions, zero_division=0),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }
    final_model_path = MODEL_PATH / "promptguard_pipeline.joblib"
    joblib.dump(pipeline, final_model_path)

    pd.DataFrame([{
        "model": "Linear SVM",
        "feature_configuration": "Char_3_5",
        "C": 1,
        "augmentation_version": SELECTED_VERSION,
        "cv_f1": float(selected_cv["f1_mean"]),
        **metrics,
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
    }]).to_csv(METRICS_PATH / "final_model_metrics.csv", index=False)

    model_information = {
        "model": "Linear SVM",
        "feature_configuration": "Char_3_5",
        "C": 1,
        "class_weight": "balanced",
        "random_state": 42,
        "augmentation_version": SELECTED_VERSION,
        "selection_metric": "External robustness",
        "selection_rationale": (
            "V3 was retained for its stronger external robustness results; "
            "the version was not selected by the highest internal CV F1."
        ),
        "cv_f1": float(selected_cv["f1_mean"]),
        **{key: float(value) for key, value in metrics.items() if key.startswith("test_")},
        **{key: int(value) for key, value in metrics.items() if not key.startswith("test_")},
        "training_samples": int(len(X_train)),
        "testing_samples": int(len(X_test)),
    }
    with open(MODEL_PATH / "model_information.json", "w", encoding="utf-8") as file:
        json.dump(model_information, file, indent=4)

    print("\n" + "=" * 70)
    print("FINAL MODEL")
    print("=" * 70)
    print("Model: Linear SVM")
    print("Features: Char_3_5")
    print("C: 1")
    print("Augmentation:", SELECTED_VERSION)
    print(f"V3 CV F1 (reported, not used to choose the version): {selected_cv['f1_mean']:.4f}")
    for label, key in (("Accuracy", "test_accuracy"), ("Precision", "test_precision"),
                       ("Recall", "test_recall"), ("F1", "test_f1")):
        print(f"{label}: {metrics[key]:.4f}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print("\nSaved model:")
    print(final_model_path)

def main():
    print("\n" + "=" * 70)
    print("PROMPTGUARD AUGMENTATION EXPERIMENT")
    print("=" * 70)

    df = preprocess_dataset(load_dataset(DATA_PATH))
    X_train, X_test, y_train, y_test = split_dataset(df)
    print("\nTraining samples:", len(X_train))
    print("Testing samples :", len(X_test))

    augmentations, versions = create_training_versions(X_train, y_train)
    print("\nAugmentation samples:")
    for name, data in augmentations.items():
        print(f"{name}: {len(data)}")

    training_summary = pd.DataFrame([
        {
            "version": name,
            "training_samples": len(X),
            "benign": int((y == 0).sum()),
            "injection": int((y == 1).sum()),
            "synthetic_samples": len(X) - len(X_train),
        }
        for name, (X, y) in versions.items()
    ])
    training_summary.to_csv(METRICS_PATH / "augmentation_training_summary.csv", index=False)
    print("\n" + "=" * 70 + "\nTRAINING VERSIONS\n" + "=" * 70)
    print(training_summary.to_string(index=False))

    print("\n" + "=" * 70 + "\n5-FOLD CROSS-VALIDATION\n" + "=" * 70)
    cv_df = pd.DataFrame([
        evaluate_cv(X, y, name) for name, (X, y) in versions.items()
    ])
    cv_df.to_csv(METRICS_PATH / "augmentation_cv_comparison.csv", index=False)
    for row in cv_df.to_dict("records"):
        print(
            f"{row['version']}: Accuracy={row['accuracy_mean']:.4f} | "
            f"Precision={row['precision_mean']:.4f} | "
            f"Recall={row['recall_mean']:.4f} | F1={row['f1_mean']:.4f}"
        )

    print("\n" + "=" * 70 + "\nHELD-OUT TEST COMPARISON\n" + "=" * 70)
    test_df = pd.DataFrame([
        evaluate_test(X, y, X_test, y_test, name)
        for name, (X, y) in versions.items()
    ])
    test_df.to_csv(METRICS_PATH / "augmentation_test_comparison.csv", index=False)
    for row in test_df.to_dict("records"):
        print(
            f"{row['version']}: Accuracy={row['test_accuracy']:.4f} | "
            f"Precision={row['test_precision']:.4f} | Recall={row['test_recall']:.4f} | "
            f"F1={row['test_f1']:.4f} | FP={row['false_positives']} | FN={row['false_negatives']}"
        )

    comparison_df = cv_df.merge(test_df, on="version")
    baseline = comparison_df.loc[comparison_df["version"] == "Baseline"].iloc[0]
    comparison_df["f1_change_vs_baseline"] = comparison_df["test_f1"] - baseline["test_f1"]
    comparison_df["recall_change_vs_baseline"] = comparison_df["test_recall"] - baseline["test_recall"]
    comparison_df["fn_change_vs_baseline"] = comparison_df["false_negatives"] - baseline["false_negatives"]
    comparison_df.to_csv(METRICS_PATH / "augmentation_comparison.csv", index=False)

    selected_cv = cv_df.loc[cv_df["version"] == SELECTED_VERSION].iloc[0]
    print("\n" + "=" * 70)
    print("SELECTED AUGMENTATION VERSION")
    print("=" * 70)
    print("Version:", SELECTED_VERSION)
    print(f"V3 CV F1 (reported, not used to choose the version): {selected_cv['f1_mean']:.4f}")

    X_final, y_final = versions[SELECTED_VERSION]
    save_final_model(X_final, y_final, X_test, y_test, selected_cv)

if __name__ == "__main__":
    main()