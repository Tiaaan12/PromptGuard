from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from feature_pipeline import get_feature_configs
from models import get_models


BASE_DIR = Path(__file__).resolve().parent.parent
METRICS_PATH = BASE_DIR / "results" / "metrics"

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
SCORING = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
}
METRICS = ("accuracy", "precision", "recall", "f1")

def _make_pipeline(features, model):
    return Pipeline([("features", features), ("model", model)])

def _summarize_cv(scores):
    summary = {}
    for metric in METRICS:
        values = scores[f"test_{metric}"]
        summary[f"{metric}_mean"] = values.mean()
        summary[f"{metric}_std"] = values.std()
    return summary

def _save_metrics(dataframe, filename):
    METRICS_PATH.mkdir(parents=True, exist_ok=True)
    path = METRICS_PATH / filename
    dataframe.to_csv(path, index=False)
    print(f"Saved: {path}")
    return path

def _print_metrics(name, summary):
    print(
        f"{name}: "
        f"Accuracy={summary['accuracy_mean']:.4f} | "
        f"Precision={summary['precision_mean']:.4f} | "
        f"Recall={summary['recall_mean']:.4f} | "
        f"F1={summary['f1_mean']:.4f}"
    )

def compare_models(X_train, y_train):
    aggregate_results = []
    fold_results = []
    feature_configs = get_feature_configs()
    models = get_models()

    for feature_name, features in feature_configs.items():
        for model_name, model in models.items():
            pipeline = _make_pipeline(features, model)
            scores = cross_validate(
                pipeline,
                X_train,
                y_train,
                cv=CV,
                scoring=SCORING,
                n_jobs=-1,
                return_train_score=False,
            )

            aggregate_results.append({
                "feature_configuration": feature_name,
                "model": model_name,
                **_summarize_cv(scores),
            })

            for fold in range(CV.n_splits):
                fold_results.append({
                    "feature_configuration": feature_name,
                    "model": model_name,
                    "fold": fold + 1,
                    **{
                        metric: scores[f"test_{metric}"][fold]
                        for metric in METRICS
                    },
                })

            _print_metrics(model_name, _summarize_cv(scores))

    aggregate_df = pd.DataFrame(aggregate_results)
    fold_df = pd.DataFrame(fold_results)
    _save_metrics(aggregate_df, "model_comparison_initial.csv")
    _save_metrics(fold_df, "model_comparison_initial_folds.csv")
    return aggregate_df

def _tune_model(model_name, X_train, y_train, feature_name, model, param_grid):
    pipeline = _make_pipeline(get_feature_configs()[feature_name], model)
    search = GridSearchCV(
        pipeline,
        param_grid,
        cv=CV,
        scoring=SCORING,
        refit="f1",
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train, y_train)

    print(f"\n{'=' * 60}\n{model_name.upper()} TUNING\n{'=' * 60}")
    print("Best parameters:", search.best_params_)
    print(f"Best CV F1: {search.best_score_:.4f}")
    return search

def tune_logistic_regression(X_train, y_train):
    return _tune_model(
        "Logistic Regression",
        X_train,
        y_train,
        "Word_Char",
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        {"model__C": [0.1, 1, 10]},
    )

def tune_linear_svm(X_train, y_train):
    return _tune_model(
        "Linear SVM",
        X_train,
        y_train,
        "Char_3_5",
        LinearSVC(class_weight="balanced", random_state=42),
        {"model__C": [0.1, 1, 10]},
    )

def tune_naive_bayes(X_train, y_train):
    return _tune_model(
        "Naive Bayes",
        X_train,
        y_train,
        "Word_1_2",
        MultinomialNB(),
        {"model__alpha": [0.1, 0.5, 1.0]},
    )

def save_hyperparameter_results(lr_search, svm_search, nb_search):
    searches = [
        ("Logistic Regression", "Word_Char", "C", "model__C", lr_search),
        ("Linear SVM", "Char_3_5", "C", "model__C", svm_search),
        ("Naive Bayes", "Word_1_2", "alpha", "model__alpha", nb_search),
    ]
    all_results = []
    best_results = []

    for model_name, feature_name, parameter_name, parameter_key, search in searches:
        cv_results = pd.DataFrame(search.cv_results_)
        parameter_column = f"param_{parameter_key}"

        for _, row in cv_results.iterrows():
            all_results.append({
                "model": model_name,
                "feature_configuration": feature_name,
                "parameter": parameter_name,
                "parameter_value": row[parameter_column],
                **{
                    f"{metric}_{stat}": row[f"{stat}_test_{metric}"]
                    for metric in METRICS
                    for stat in ("mean", "std")
                },
                "rank_by_f1": row["rank_test_f1"],
            })

        best_row = cv_results.iloc[search.best_index_]
        best_results.append({
            "model": model_name,
            "feature_configuration": feature_name,
            "parameter": parameter_name,
            "best_value": search.best_params_[parameter_key],
            **{
                f"{metric}_{stat}": best_row[f"{stat}_test_{metric}"]
                for metric in METRICS
                for stat in ("mean", "std")
            },
        })

    all_df = pd.DataFrame(all_results)
    best_df = pd.DataFrame(best_results)
    _save_metrics(all_df, "hyperparameter_tuning_all.csv")
    _save_metrics(best_df, "hyperparameter_tuning_best.csv")
    return all_df, best_df

def run_feature_ablation(X_train, y_train):
    print("\n" + "#" * 60 + "\n# FEATURE ENGINEERING ABLATION\n" + "#" * 60)
    configs = get_feature_configs()
    feature_configs = {
        "Simple_Word_Unigram": TfidfVectorizer(
            analyzer="word",
            lowercase=True,
            ngram_range=(1, 1),
            min_df=2,
            sublinear_tf=True,
        ),
        "Word_1_2": configs["Word_1_2"],
        "Word_1_3": configs["Word_1_3"],
        "Char_3_5": configs["Char_3_5"],
        "Word_Char": configs["Word_Char"],
    }

    results = []
    for feature_name, features in feature_configs.items():
        model = LogisticRegression(
            C=1,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )
        scores = cross_validate(
            _make_pipeline(features, model),
            X_train,
            y_train,
            cv=CV,
            scoring=SCORING,
            n_jobs=-1,
            return_train_score=False,
        )
        result = {"feature_configuration": feature_name, **_summarize_cv(scores)}
        results.append(result)
        _print_metrics(feature_name, result)

    results_df = pd.DataFrame(results)
    baseline_f1 = results_df.loc[
        results_df["feature_configuration"] == "Simple_Word_Unigram", "f1_mean"
    ].iloc[0]
    results_df["f1_change_vs_simple"] = results_df["f1_mean"] - baseline_f1
    _save_metrics(results_df, "feature_ablation.csv")
    return results_df

def get_final_pipeline(C=10):
    return _make_pipeline(
        get_feature_configs()["Word_Char"],
        LogisticRegression(
            C=C,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
    )
