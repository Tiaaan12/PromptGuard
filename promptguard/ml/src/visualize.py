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