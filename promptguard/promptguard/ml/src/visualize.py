import matplotlib.pyplot as plt
import seaborn as sns


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
    plt.title("Class Distribution of Prompt Samples")

    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()