from pathlib import Path

import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
    GridSearchCV
)

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics import (
    make_scorer,
    precision_score,
    recall_score,
    f1_score
)

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

from feature_pipeline import get_feature_configs
from models import get_models


# ============================================================
# PATHS
# ============================================================

# train.py is inside:
# ml/src/
#
# parent = src
# parent.parent = ml

BASE_DIR = Path(__file__).resolve().parent.parent

METRICS_PATH = BASE_DIR / "results" / "metrics"


# ============================================================
# CROSS-VALIDATION SETTINGS
# ============================================================

CV = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# ============================================================
# SCORING METRICS
# ============================================================

SCORING = {
    "accuracy": "accuracy",

    "precision": make_scorer(
        precision_score,
        zero_division=0
    ),

    "recall": make_scorer(
        recall_score,
        zero_division=0
    ),

    "f1": make_scorer(
        f1_score,
        zero_division=0
    )
}


# ============================================================
# INITIAL MODEL + FEATURE COMPARISON
# ============================================================

def compare_models(X_train, y_train):

    feature_configs = get_feature_configs()
    models = get_models()

    aggregate_results = []
    fold_results = []

    for feature_name, features in feature_configs.items():

        print("\n" + "=" * 60)
        print(f"FEATURE CONFIGURATION: {feature_name}")
        print("=" * 60)

        for model_name, model in models.items():

            pipeline = Pipeline([
                ("features", features),
                ("model", model)
            ])

            scores = cross_validate(
                pipeline,
                X_train,
                y_train,
                cv=CV,
                scoring=SCORING,
                n_jobs=-1,
                return_train_score=False
            )

            # ------------------------------------------------
            # MEAN + STANDARD DEVIATION
            # ------------------------------------------------

            aggregate_results.append({
                "feature_configuration": feature_name,
                "model": model_name,

                "accuracy_mean":
                    scores["test_accuracy"].mean(),

                "accuracy_std":
                    scores["test_accuracy"].std(),

                "precision_mean":
                    scores["test_precision"].mean(),

                "precision_std":
                    scores["test_precision"].std(),

                "recall_mean":
                    scores["test_recall"].mean(),

                "recall_std":
                    scores["test_recall"].std(),

                "f1_mean":
                    scores["test_f1"].mean(),

                "f1_std":
                    scores["test_f1"].std()
            })

            # ------------------------------------------------
            # INDIVIDUAL FOLD RESULTS
            # ------------------------------------------------

            for fold in range(CV.n_splits):

                fold_results.append({
                    "feature_configuration":
                        feature_name,

                    "model":
                        model_name,

                    "fold":
                        fold + 1,

                    "accuracy":
                        scores["test_accuracy"][fold],

                    "precision":
                        scores["test_precision"][fold],

                    "recall":
                        scores["test_recall"][fold],

                    "f1":
                        scores["test_f1"][fold]
                })

            # ------------------------------------------------
            # TERMINAL OUTPUT
            # ------------------------------------------------

            print(
                f"{model_name}: "
                f"Accuracy={scores['test_accuracy'].mean():.4f} | "
                f"Precision={scores['test_precision'].mean():.4f} | "
                f"Recall={scores['test_recall'].mean():.4f} | "
                f"F1={scores['test_f1'].mean():.4f}"
            )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    METRICS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    aggregate_df = pd.DataFrame(
        aggregate_results
    )

    fold_df = pd.DataFrame(
        fold_results
    )

    aggregate_df.to_csv(
        METRICS_PATH / "model_comparison_initial.csv",
        index=False
    )

    fold_df.to_csv(
        METRICS_PATH / "model_comparison_initial_folds.csv",
        index=False
    )

    print("\nInitial comparison saved:")
    print(
        METRICS_PATH /
        "model_comparison_initial.csv"
    )

    print("\nFold-level results saved:")
    print(
        METRICS_PATH /
        "model_comparison_initial_folds.csv"
    )

    return aggregate_df


# ============================================================
# LOGISTIC REGRESSION TUNING
# ============================================================

def tune_logistic_regression(X_train, y_train):

    features = get_feature_configs()["Word_Char"]

    pipeline = Pipeline([
        ("features", features),

        (
            "model",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    param_grid = {
        "model__C": [0.1, 1, 10]
    }

    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=CV,
        scoring=SCORING,
        refit="f1",
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    print("\n" + "=" * 60)
    print("LOGISTIC REGRESSION TUNING")
    print("=" * 60)

    print("Best parameters:")
    print(
        grid_search.best_params_
    )

    print("Best CV F1:")
    print(
        f"{grid_search.best_score_:.4f}"
    )

    return grid_search


# ============================================================
# LINEAR SVM TUNING
# ============================================================

def tune_linear_svm(X_train, y_train):

    features = get_feature_configs()["Char_3_5"]

    pipeline = Pipeline([
        ("features", features),

        (
            "model",
            LinearSVC(
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    param_grid = {
        "model__C": [0.1, 1, 10]
    }

    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=CV,
        scoring=SCORING,
        refit="f1",
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    print("\n" + "=" * 60)
    print("LINEAR SVM TUNING")
    print("=" * 60)

    print("Best parameters:")
    print(
        grid_search.best_params_
    )

    print("Best CV F1:")
    print(
        f"{grid_search.best_score_:.4f}"
    )

    return grid_search


# ============================================================
# NAIVE BAYES TUNING
# ============================================================

def tune_naive_bayes(X_train, y_train):

    features = get_feature_configs()["Word_1_2"]

    pipeline = Pipeline([
        ("features", features),

        (
            "model",
            MultinomialNB()
        )
    ])

    param_grid = {
        "model__alpha": [0.1, 0.5, 1.0]
    }

    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=CV,
        scoring=SCORING,
        refit="f1",
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train
    )

    print("\n" + "=" * 60)
    print("NAIVE BAYES TUNING")
    print("=" * 60)

    print("Best parameters:")
    print(
        grid_search.best_params_
    )

    print("Best CV F1:")
    print(
        f"{grid_search.best_score_:.4f}"
    )

    return grid_search


# ============================================================
# SAVE ALL HYPERPARAMETER RESULTS
# ============================================================

def save_hyperparameter_results(
    lr_search,
    svm_search,
    nb_search
):

    all_results = []
    best_results = []

    # --------------------------------------------------------
    # Each tuple contains:
    #
    # Model name
    # Feature configuration
    # Parameter display name
    # Parameter dictionary key
    # cv_results_ parameter column
    # GridSearch object
    # --------------------------------------------------------

    searches = [

        (
            "Logistic Regression",
            "Word_Char",
            "C",
            "model__C",
            "param_model__C",
            lr_search
        ),

        (
            "Linear SVM",
            "Char_3_5",
            "C",
            "model__C",
            "param_model__C",
            svm_search
        ),

        (
            "Naive Bayes",
            "Word_1_2",
            "alpha",
            "model__alpha",
            "param_model__alpha",
            nb_search
        )
    ]

    for (
        model_name,
        feature_name,
        parameter_name,
        parameter_key,
        cv_parameter_column,
        search
    ) in searches:

        cv_df = pd.DataFrame(
            search.cv_results_
        )

        # ----------------------------------------------------
        # SAVE EVERY TESTED PARAMETER VALUE
        # ----------------------------------------------------

        for _, row in cv_df.iterrows():

            all_results.append({
                "model":
                    model_name,

                "feature_configuration":
                    feature_name,

                "parameter":
                    parameter_name,

                "parameter_value":
                    row[cv_parameter_column],

                "accuracy_mean":
                    row["mean_test_accuracy"],

                "accuracy_std":
                    row["std_test_accuracy"],

                "precision_mean":
                    row["mean_test_precision"],

                "precision_std":
                    row["std_test_precision"],

                "recall_mean":
                    row["mean_test_recall"],

                "recall_std":
                    row["std_test_recall"],

                "f1_mean":
                    row["mean_test_f1"],

                "f1_std":
                    row["std_test_f1"],

                "rank_by_f1":
                    row["rank_test_f1"]
            })

        # ----------------------------------------------------
        # SAVE BEST PARAMETER FOR EACH MODEL
        # ----------------------------------------------------

        best_index = search.best_index_

        best_row = cv_df.iloc[
            best_index
        ]

        best_results.append({
            "model":
                model_name,

            "feature_configuration":
                feature_name,

            "parameter":
                parameter_name,

            "best_value":
                search.best_params_[parameter_key],

            "accuracy_mean":
                best_row["mean_test_accuracy"],

            "accuracy_std":
                best_row["std_test_accuracy"],

            "precision_mean":
                best_row["mean_test_precision"],

            "precision_std":
                best_row["std_test_precision"],

            "recall_mean":
                best_row["mean_test_recall"],

            "recall_std":
                best_row["std_test_recall"],

            "f1_mean":
                best_row["mean_test_f1"],

            "f1_std":
                best_row["std_test_f1"]
        })

    all_df = pd.DataFrame(
        all_results
    )

    best_df = pd.DataFrame(
        best_results
    )

    METRICS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    # All parameter values
    all_df.to_csv(
        METRICS_PATH /
        "hyperparameter_tuning_all.csv",
        index=False
    )

    # Best value per model
    best_df.to_csv(
        METRICS_PATH /
        "hyperparameter_tuning_best.csv",
        index=False
    )

    print("\nHyperparameter results saved:")
    print(
        METRICS_PATH /
        "hyperparameter_tuning_all.csv"
    )

    print(
        METRICS_PATH /
        "hyperparameter_tuning_best.csv"
    )

    return all_df, best_df


# ============================================================
# FEATURE ENGINEERING ABLATION
# ============================================================

def run_feature_ablation(X_train, y_train):

    print("\n" + "#" * 60)
    print("# FEATURE ENGINEERING ABLATION")
    print("#" * 60)

    # --------------------------------------------------------
    # SIMPLE BASELINE FEATURE REPRESENTATION
    #
    # This represents a simpler text representation:
    # Word-level TF-IDF using only unigrams.
    # --------------------------------------------------------

    simple_word = TfidfVectorizer(
        analyzer="word",
        lowercase=True,
        ngram_range=(1, 1),
        min_df=2,
        sublinear_tf=True
    )

    feature_configs = {
        "Simple_Word_Unigram":
            simple_word,

        "Word_1_2":
            get_feature_configs()["Word_1_2"],

        "Word_1_3":
            get_feature_configs()["Word_1_3"],

        "Char_3_5":
            get_feature_configs()["Char_3_5"],

        "Word_Char":
            get_feature_configs()["Word_Char"]
    }

    results = []

    for feature_name, features in feature_configs.items():

        # Fresh classifier for every experiment
        model = LogisticRegression(
            C=1,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )

        pipeline = Pipeline([
            ("features", features),
            ("model", model)
        ])

        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=CV,
            scoring=SCORING,
            n_jobs=-1,
            return_train_score=False
        )

        result = {
            "feature_configuration":
                feature_name,

            "accuracy_mean":
                scores["test_accuracy"].mean(),

            "accuracy_std":
                scores["test_accuracy"].std(),

            "precision_mean":
                scores["test_precision"].mean(),

            "precision_std":
                scores["test_precision"].std(),

            "recall_mean":
                scores["test_recall"].mean(),

            "recall_std":
                scores["test_recall"].std(),

            "f1_mean":
                scores["test_f1"].mean(),

            "f1_std":
                scores["test_f1"].std()
        }

        results.append(
            result
        )

        print(
            f"{feature_name}: "
            f"Accuracy={result['accuracy_mean']:.4f} | "
            f"Precision={result['precision_mean']:.4f} | "
            f"Recall={result['recall_mean']:.4f} | "
            f"F1={result['f1_mean']:.4f}"
        )

    # --------------------------------------------------------
    # CALCULATE F1 CHANGE RELATIVE TO SIMPLE BASELINE
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    simple_f1 = results_df.loc[
        results_df["feature_configuration"]
        == "Simple_Word_Unigram",
        "f1_mean"
    ].iloc[0]

    results_df["f1_change_vs_simple"] = (
        results_df["f1_mean"] -
        simple_f1
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    METRICS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    results_df.to_csv(
        METRICS_PATH /
        "feature_ablation.csv",
        index=False
    )

    print("\nFeature ablation saved:")
    print(
        METRICS_PATH /
        "feature_ablation.csv"
    )

    return results_df


# ============================================================
# FINAL PIPELINE
# ============================================================

def get_final_pipeline(C=10):

    features = get_feature_configs()["Word_Char"]

    pipeline = Pipeline([
        ("features", features),

        (
            "model",
            LogisticRegression(
                C=C,
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    return pipeline