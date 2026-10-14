import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay
)

from data_preprocessing import (
    load_dataset,
    preprocess_dataset,
    split_dataset
)

import joblib
import pandas as pd
import numpy as np
from pathlib import Path

def plot_class_distribution(df, output_path):
    
    class_counts = df["label"].value_counts()
    total = class_counts.sum()

    plt.figure(figsize=(8, 5))

    ax = sns.barplot(
        x=class_counts.index,
        y=class_counts.values,
        hue=class_counts.index,
        palette=["#2A6F97", "#E07A5F"],
        legend=False
    )

    for i, count in enumerate(class_counts.values):
        percentage = (count / total) * 100

        ax.text(
            i,
            count + total * 0.01,
            f"{count:,} ({percentage:.1f}%)",
            ha="center",
            fontsize=10
        )

    plt.xlabel("Class")
    plt.ylabel("Number of Samples")

    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_length_by_class(df, output_path):
    plt.figure(figsize=(9, 5))

    sns.boxplot(
        data=df,
        x="label",
        y="word_count",
        palette=["#2A6F97", "#E07A5F"],
    )

    plt.xlabel("Prompt Label")
    plt.ylabel("Word Count")
    plt.ylim(0, df["word_count"].quantile(0.95))

    plt.tight_layout()
   
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_category_distribution(df, output_path):
    plt.figure(figsize=(10, 6))

    order = df[df["label"] == "injection"]["category"].value_counts().index

    sns.countplot(
        data=df[df["label"] == "injection"],
        y="category",
        order=order,
        
)

    plt.xlabel("Number of Prompts")
    plt.ylabel("Injection Category")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_internal_test_confusion_matrix(
    dataset_path,
    model_path,
    output_path
):
    df = load_dataset(dataset_path)
    df = preprocess_dataset(df)

    _, X_test, _, y_test = split_dataset(df)

    model = joblib.load(model_path)

    y_pred = model.predict(X_test)

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    print("\nInternal Test Confusion Matrix:")
    print(cm)

    fig, ax = plt.subplots(
        figsize=(5, 4)
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=[
            "Benign",
            "Injection"
        ]
    )

    display.plot(
        ax=ax,
        values_format="d"
    )

    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        "\nSaved:",
        output_path
    )


def plot_baseline_confusion_matrix(
    predictions_path,
    output_path,
):
    df = pd.read_csv(predictions_path)

    cm = confusion_matrix(
        df["actual"],
        df["predicted"],
        labels=[0, 1],
    )

    print("\nBaseline Internal Test Confusion Matrix:")
    print(cm)

    fig, ax = plt.subplots(figsize=(5, 4))

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Benign", "Injection"],
    )

    display.plot(
        ax=ax,
        values_format="d",
        cmap="Blues",
    )

    ax.set_title("Baseline Model — Internal Test Set")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

def plot_external_f1_progression(
    results_path,
    output_path
):
    results = pd.read_csv(results_path)

    version_order = [
        "Baseline",
        "V1",
        "V2",
        "V3"
    ]

    results["version"] = pd.Categorical(
        results["version"],
        categories=version_order,
        ordered=True
    )

    results = results.sort_values(
        "version"
    )

    plt.figure(
        figsize=(7, 4.5)
    )

    plt.plot(
        results["version"],
        results["f1"],
        marker="o",
        linewidth=2
    )

    for x, y in zip(
        results["version"],
        results["f1"]
    ):
        plt.text(
            x,
            y + 0.02,
            f"{y:.4f}",
            ha="center",
            fontsize=9
        )

    plt.xlabel(
        "Augmentation Version"
    )

    plt.ylabel(
        "F1-Score"
    )

    plt.ylim(
        0,
        1
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def plot_svm_top_coefficients(
    model_path,
    output_path,
    top_n=12
):
    pipeline = joblib.load(model_path)
    if not hasattr(pipeline, "steps") or len(pipeline.steps) < 2:
        raise ValueError(
            "Expected a fitted sklearn Pipeline."
        )

    classifier = pipeline.steps[-1][1]

    if not hasattr(classifier, "coef_"):
        raise TypeError(
            "The final model does not expose linear coefficients."
        )

    if list(classifier.classes_) != [0, 1]:
        raise ValueError(
            "Expected binary classes ordered as [0, 1]."
        )

    feature_transformer = pipeline[:-1]
    feature_names = feature_transformer.get_feature_names_out()
    coefficients = np.asarray(
        classifier.coef_
    ).ravel()

    if len(feature_names) != len(coefficients):
        raise ValueError(
            "Feature names and model coefficients do not match."
        )

    n = min(top_n, len(coefficients) // 2)

    negative_indices = np.argsort(coefficients)[:n]
    positive_indices = np.argsort(coefficients)[-n:]

    indices = np.concatenate([
        negative_indices,
        positive_indices
    ])

    values = coefficients[indices]

 
    labels = []

    for index in indices:
        name = str(feature_names[index])

        if "__" in name:
            name = name.split("__", 1)[1]

        name = (
            name.replace(" ", "·")
                .replace("\n", "↵")
                .replace("\t", "⇥")
        )

        labels.append(name)

    order = np.argsort(values)
    values = values[order]
    labels = [
        labels[i] for i in order
    ]

    fig, ax = plt.subplots(
        figsize=(8, 7)
    )

    ax.barh(
        labels,
        values
    )

    ax.axvline(
        0,
        linewidth=0.8
    )

    ax.set_xlabel(
        "Linear SVM coefficient "
        "(negative: benign, positive: injection)"
    )

    ax.set_ylabel(
        "Character n-gram"
    )

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        "Saved coefficient visualization:",
        output_path
    )

    return indices

def plot_prompt_length_distribution(df, output_path):

    if "word_count" in df.columns:
        lengths = pd.to_numeric(
            df["word_count"],
            errors="coerce"
        )
    else:
        lengths = (
            df["text"]
            .fillna("")
            .astype(str)
            .str.split()
            .str.len()
        )

    lengths = lengths.dropna()

    fig, ax = plt.subplots(figsize=(6, 3.5))

    sns.histplot(
        x=lengths,
        bins=40,
        color="#2A6F97",
        ax=ax
    )

    median_length = lengths.median()

    ax.axvline(
        median_length,
        linestyle="--",
        color="#E07A5F",
        linewidth=1.5,
        label=f"Median: {median_length:.0f} words"
    )

    ax.set_xlabel("Prompt Length (Words)")
    ax.set_ylabel("Number of Prompts")
    ax.legend(frameon=False)

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved: {output_path}")

def plot_class_distribution_by_category(
    df,
    output_path,
    category_column="category",
    top_n=8
):
    if category_column not in df.columns:
        raise ValueError(
            f"Column '{category_column}' not found in dataset."
        )

    required = [category_column, "label"]

    data = df[required].copy()

    data[category_column] = (
        data[category_column]
        .fillna("Unknown")
        .astype(str)
    )

    data["label"] = (
        data["label"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    data = data[
        data["label"].isin(["benign", "injection"])
    ]

    category_counts = (
        data[category_column]
        .value_counts()
    )

    top_categories = category_counts.head(top_n).index

    data = data[
        data[category_column].isin(top_categories)
    ]

    distribution = pd.crosstab(
        data[category_column],
        data["label"],
        normalize="index"
    ) * 100

    distribution = distribution.reindex(
        index=top_categories,
        columns=["benign", "injection"],
        fill_value=0
    )

    counts = (
        data[category_column]
        .value_counts()
        .reindex(top_categories)
    )

    labels = [
        f"{category} (n={counts[category]})"
        for category in top_categories
    ]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.barh(
        labels,
        distribution["benign"],
        label="Benign",
        color="#2A6F97"
    )

    ax.barh(
        labels,
        distribution["injection"],
        left=distribution["benign"],
        label="Injection",
        color="#E07A5F"
    )

    ax.set_xlabel("Prompts Within Category (%)")
    ax.set_ylabel("Category")
    ax.set_xlim(0, 100)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
        frameon=False
    )

    ax.invert_yaxis()

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved: {output_path}")