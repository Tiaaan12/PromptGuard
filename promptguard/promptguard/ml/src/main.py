from data_preprocessing import load_dataset, preprocess_dataset, split_dataset


df = load_dataset("../data/raw/kaggle.csv")
preprocessed_df = preprocess_dataset(df)
X_train, X_test, y_train, y_test = split_dataset(preprocessed_df)