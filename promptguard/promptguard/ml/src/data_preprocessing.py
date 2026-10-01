import pandas as pd
from sklearn.model_selection import train_test_split


def load_dataset(path):
    return pd.read_csv(path)


def preprocess_dataset(df):

    df = df[["text", "label"]].copy()

    df["text"] = df["text"].astype(str).str.strip()

    df = df.dropna(subset=["text", "label"])

    df["target"] = df["label"].map({
        "benign": 0,
        "injection": 1
    })

    df = df.dropna(subset=["target"])

    df["target"] = df["target"].astype(int)

    df.to_csv('../data/processed/preprocessed_internal_dataset.csv', index=False)

    print(df.head())
    return df




def split_dataset(df):

    X = df["text"]
    y = df["target"]

    return train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )