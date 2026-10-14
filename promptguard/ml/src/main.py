from pathlib import Path
import json

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from data_preprocessing import load_dataset, preprocess_dataset, split_dataset
from train import (
    compare_models,
    tune_logistic_regression,
    tune_linear_svm,
    tune_naive_bayes,
    save_hyperparameter_results,
    run_feature_ablation,
)
from visualize import (
    plot_class_distribution,
    plot_internal_test_confusion_matrix,
    plot_external_f1_progression,
    plot_category_distribution,
    plot_length_by_class,
    plot_svm_top_coefficients,
    plot_class_distribution_by_category,
    plot_prompt_length_distribution,
    plot_baseline_confusion_matrix
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "internal_dataset.csv"
RESULTS_PATH = BASE_DIR / "results"
METRICS_PATH = RESULTS_PATH / "metrics"
ERRORS_PATH = RESULTS_PATH / "errors"
VISUALIZATION_PATH = RESULTS_PATH / "visualizations"
MODEL_PATH = BASE_DIR / "model" / "promptguard_pipeline.joblib"

TEST_SIZE = 0.20
SPLIT_RANDOM_STATE = 42
CV_RANDOM_STATE = 42

def create_output_directories():
    for path in (METRICS_PATH, ERRORS_PATH, VISUALIZATION_PATH):
        path.mkdir(parents=True, exist_ok=True)


def generate_visualizations(raw_df):
    print("\nGenerating visualizations...")
    plot_baseline_confusion_matrix(
    predictions_path=(
        RESULTS_PATH / "errors" / "baseline_predictions.csv"
    ),
    output_path=(
        VISUALIZATION_PATH / "baseline_confusion_matrix.png"
    ),
)
    plot_prompt_length_distribution(
        raw_df,
        VISUALIZATION_PATH / "prompt_length_distribution.png",
    )
    plot_class_distribution_by_category(
        raw_df,
        output_path=VISUALIZATION_PATH / "class_distribution_by_category.png",
        category_column="category",
        top_n=8,
    )
    plot_length_by_class(
        raw_df,
        VISUALIZATION_PATH / "prompt_length_by_class.png",
    )
    plot_category_distribution(
        raw_df,
        VISUALIZATION_PATH / "prompt_category_distribution.png",
    )
    plot_class_distribution(
        raw_df,
        VISUALIZATION_PATH / "class_distribution.png",
    )
    if MODEL_PATH.exists():
        for title, plot_function, kwargs in (
            (
                "SVM feature coefficients",
                plot_svm_top_coefficients,
                {
                    "model_path": MODEL_PATH,
                    "output_path": VISUALIZATION_PATH / "svm_top_coefficients.png",
                },
            ),
            (
                "internal test confusion matrix",
                plot_internal_test_confusion_matrix,
                {
                    "dataset_path": DATA_PATH,
                    "model_path": MODEL_PATH,
                    "output_path": VISUALIZATION_PATH / "internal_test_confusion_matrix.png",
                },
            ),
        ):
            try:
                plot_function(**kwargs)
            except (ValueError, TypeError, AttributeError, KeyError) as exc:
                print(f"Skipped {title}: {exc}")
    else:
        print(f"Skipped model-dependent plots; model not found: {MODEL_PATH}")

    external_results_path = METRICS_PATH / "external_evaluation.csv"
    if external_results_path.exists():
        try:
            plot_external_f1_progression(
                results_path=external_results_path,
                output_path=VISUALIZATION_PATH / "external_f1_progression.png",
            )
        except (ValueError, TypeError, KeyError) as exc:
            print(f"Skipped external F1 plot: {exc}")
    else:
        print(f"Skipped external F1 plot; results not found: {external_results_path}")

def save_split_summary(y_train, y_test):
    rows = []
    for subset_name, labels in (("train", y_train), ("test", y_test)):
        rows.append(
            {
                "dataset_part": subset_name,
                "samples": len(labels),
                "benign": int((labels == 0).sum()),
                "injection": int((labels == 1).sum()),
            }
        )
    pd.DataFrame(rows).to_csv(
        METRICS_PATH / "dataset_split_summary.csv",
        index=False,
    )

def save_experiment_configuration(df, X_train, X_test):
    configuration = {
        "dataset": DATA_PATH.name,
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_size": TEST_SIZE,
        "split_random_state": SPLIT_RANDOM_STATE,
        "cross_validation": "5-fold StratifiedKFold",
        "cv_shuffle": True,
        "cv_random_state": CV_RANDOM_STATE,
        "model_selection_metric": "F1-score",
        "initial_models": [
            "Logistic Regression",
            "Linear SVM",
            "Naive Bayes",
        ],
        "initial_features": [
            "Word_1_2",
            "Word_1_3",
            "Char_3_5",
            "Word_Char",
        ],
        "hyperparameters": {
            "Logistic Regression": {"C": [0.1, 1, 10]},
            "Linear SVM": {"C": [0.1, 1, 10]},
            "Naive Bayes": {"alpha": [0.1, 0.5, 1.0]},
        },
    }

    with open(
        METRICS_PATH / "experiment_configuration.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(configuration, file, indent=4)

def report_initial_best(initial_results):
    best = initial_results.loc[initial_results["f1_mean"].idxmax()]

    print("\n" + "=" * 60)
    print("INITIAL BEST CONFIGURATION")
    print("=" * 60)
    print(f"Feature:   {best['feature_configuration']}")
    print(f"Model:     {best['model']}")
    print(f"Accuracy:  {best['accuracy_mean']:.4f}")
    print(f"Precision: {best['precision_mean']:.4f}")
    print(f"Recall:    {best['recall_mean']:.4f}")
    print(f"F1:        {best['f1_mean']:.4f}")


def run_hyperparameter_tuning(X_train, y_train):
    print("\n" + "#" * 60)
    print("# HYPERPARAMETER TUNING")
    print("#" * 60)

    lr_search = tune_logistic_regression(X_train, y_train)
    svm_search = tune_linear_svm(X_train, y_train)
    nb_search = tune_naive_bayes(X_train, y_train)
    tuning_all, tuning_best = save_hyperparameter_results(
        lr_search,
        svm_search,
        nb_search,
    )

    print("\n" + "=" * 60)
    print("FINAL TUNED MODEL COMPARISON")
    print("=" * 60)
    print(f"Logistic Regression: {lr_search.best_score_:.4f}")
    print(f"Linear SVM:          {svm_search.best_score_:.4f}")
    print(f"Naive Bayes:         {nb_search.best_score_:.4f}")

    searches = [
        ("Logistic Regression", "Word_Char", lr_search),
        ("Linear SVM", "Char_3_5", svm_search),
        ("Naive Bayes", "Word_1_2", nb_search),
    ]
    final_model_name, final_feature_name, final_search = max(
        searches,
        key=lambda item: item[2].best_score_,
    )

    print("\n" + "=" * 60)
    print("FINAL CORE MODEL SELECTED BY CV F1")
    print("=" * 60)
    print(f"Model:                 {final_model_name}")
    print(f"Feature configuration: {final_feature_name}")
    print(f"Best parameters:       {final_search.best_params_}")
    print(f"CV F1:                 {final_search.best_score_:.4f}")

    return (
        lr_search,
        svm_search,
        nb_search,
        tuning_all,
        tuning_best,
        final_model_name,
        final_feature_name,
        final_search,
    )

def save_model_selection_summary(initial_results, tuning_best, final_model_name):
    initial_best_by_model = (
        initial_results.sort_values(
            ["model", "f1_mean"],
            ascending=[True, False],
        )
        .drop_duplicates(subset=["model"])
    )
    rows = []
    for _, row in initial_best_by_model.iterrows():
        rows.append(
            {
                "stage": "Initial comparison",
                "model": row["model"],
                "feature_configuration": row["feature_configuration"],
                "parameter": "",
                "parameter_value": "",
                "accuracy": row["accuracy_mean"],
                "precision": row["precision_mean"],
                "recall": row["recall_mean"],
                "f1": row["f1_mean"],
                "f1_std": row["f1_std"],
                "selected_final": False,
            }
        )
    for _, row in tuning_best.iterrows():
        rows.append(
            {
                "stage": "After hyperparameter tuning",
                "model": row["model"],
                "feature_configuration": row["feature_configuration"],
                "parameter": row["parameter"],
                "parameter_value": row["best_value"],
                "accuracy": row["accuracy_mean"],
                "precision": row["precision_mean"],
                "recall": row["recall_mean"],
                "f1": row["f1_mean"],
                "f1_std": row["f1_std"],
                "selected_final": row["model"] == final_model_name,
            }
        )
    pd.DataFrame(rows).to_csv(
        METRICS_PATH / "model_selection_summary.csv",
        index=False,
    )

def evaluate_selected_model(final_search, model_name, feature_name, X_train, X_test, y_test):
    pipeline = final_search.best_estimator_
    predictions = pipeline.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
    }
    cm = confusion_matrix(y_test, predictions, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    print("\n" + "=" * 60)
    print("HELD-OUT INTERNAL TEST RESULTS")
    print("=" * 60)
    for name, value in metrics.items():
        print(f"{name.capitalize():10s}: {value:.4f}")
    print("\nConfusion matrix [ [TN, FP], [FN, TP] ]:")
    print(cm)
    print(f"TN: {tn} | FP: {fp} | FN: {fn} | TP: {tp}")

    pd.DataFrame(
        [
            {
                "model": model_name,
                "feature_configuration": feature_name,
                "parameters": str(final_search.best_params_),
                **metrics,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp,
                "test_samples": len(X_test),
            }
        ]
    ).to_csv(METRICS_PATH / "baseline_metrics.csv", index=False)

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["benign", "injection"],
        output_dict=True,
        zero_division=0,
    )
    pd.DataFrame(report).transpose().to_csv(
        METRICS_PATH / "baseline_classification_report.csv"
    )

    pd.DataFrame(
        cm,
        index=["actual_benign", "actual_injection"],
        columns=["predicted_benign", "predicted_injection"],
    ).to_csv(METRICS_PATH / "baseline_confusion_matrix.csv")

    errors = pd.DataFrame(
        {
            "text": X_test.reset_index(drop=True),
            "actual": y_test.reset_index(drop=True),
            "predicted": pd.Series(predictions),
        }
    )
    errors["error_type"] = "correct"
    errors.loc[(errors["actual"] == 0) & (errors["predicted"] == 1), "error_type"] = "false_positive"
    errors.loc[(errors["actual"] == 1) & (errors["predicted"] == 0), "error_type"] = "false_negative"

    if hasattr(pipeline, "decision_function"):
        errors["model_score"] = pipeline.decision_function(X_test)
    elif hasattr(pipeline, "predict_proba"):
        errors["model_score"] = pipeline.predict_proba(X_test)[:, 1]

    errors.to_csv(ERRORS_PATH / "baseline_errors.csv", index=False)
    errors[errors["error_type"] == "false_negative"].to_csv(
        ERRORS_PATH / "baseline_false_negatives.csv",
        index=False,
    )
    errors[errors["error_type"] == "false_positive"].to_csv(
        ERRORS_PATH / "baseline_false_positives.csv",
        index=False,
    )

    model_info = {
        "model": model_name,
        "feature_configuration": feature_name,
        "best_parameters": final_search.best_params_,
        "cross_validation_f1": final_search.best_score_,
        "test_accuracy": metrics["accuracy"],
        "test_precision": metrics["precision"],
        "test_recall": metrics["recall"],
        "test_f1": metrics["f1"],
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
    }
    with open(
        METRICS_PATH / "final_model_information.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(model_info, file, indent=4)


def main():
    create_output_directories()
    print("=" * 60)
    print("DATASET")
    print("=" * 60)
    raw_df = load_dataset(DATA_PATH)
    print("Original shape:", raw_df.shape)
    generate_visualizations(raw_df)

    df = preprocess_dataset(raw_df.copy())
    print("\nProcessed shape:", df.shape)
    X_train, X_test, y_train, y_test = split_dataset(df)
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")
    print("\nTraining distribution:")
    print(y_train.value_counts())
    print("\nTesting distribution:")
    print(y_test.value_counts())

    save_split_summary(y_train, y_test)
    save_experiment_configuration(df, X_train, X_test)

    print("\n" + "#" * 60)
    print("# INITIAL MODEL + FEATURE COMPARISON (UNTUNED)")
    print("#" * 60)
    initial_results = compare_models(X_train, y_train)
    report_initial_best(initial_results)

    print("\n" + "#" * 60)
    print("# FEATURE ENGINEERING ABLATION")
    print("#" * 60)
    run_feature_ablation(X_train, y_train)

    (
        _lr_search,
        _svm_search,
        _nb_search,
        _tuning_all,
        tuning_best,
        final_model_name,
        final_feature_name,
        final_search,
    ) = run_hyperparameter_tuning(X_train, y_train)
    save_model_selection_summary(
        initial_results,
        tuning_best,
        final_model_name,
    )

    evaluate_selected_model(
        final_search,
        final_model_name,
        final_feature_name,
        X_train,
        X_test,
        y_test,
    )

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print("Metrics saved to:", METRICS_PATH)
    print("Errors saved to:", ERRORS_PATH)
    print("Visualizations saved to:", VISUALIZATION_PATH)
    print("\nMetric files generated/updated:")
    for name in (
        "dataset_split_summary.csv",
        "experiment_configuration.json",
        "model_comparison_initial.csv",
        "model_comparison_initial_folds.csv",
        "feature_ablation.csv",
        "hyperparameter_tuning_all.csv",
        "hyperparameter_tuning_best.csv",
        "model_selection_summary.csv",
        "baseline_metrics.csv",
        "baseline_classification_report.csv",
        "baseline_confusion_matrix.csv",
        "final_model_information.json",
    ):
        print(" -", name)
    print("\nError files generated/updated:")
    for name in (
        "baseline_errors.csv",
        "baseline_false_negatives.csv",
        "baseline_false_positives.csv",
    ):
        print(" -", name)

if __name__ == "__main__":
    main()
