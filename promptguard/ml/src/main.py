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
.
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



if __name__ == "__main__":
    main()
