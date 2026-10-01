from data_preprocessing import load_dataset, preprocess_dataset, split_dataset
from visualize import plot_class_distribution
from augmentation import create_augmentation_v1, save_augmentation

DATA_PATH = "../data/raw/internal_dataset.csv"
VISUALIZATION_DIR = "../results/visualizations"

df = load_dataset(DATA_PATH)
preprocessed_df = preprocess_dataset(df)
X_train, X_test, y_train, y_test = split_dataset(preprocessed_df)

plot_class_distribution(preprocessed_df, f"{VISUALIZATION_DIR}/class_distribution.png")

augmentation_v1 = create_augmentation_v1()

save_augmentation(augmentation_v1, "../data/augmented/augmentation_v1.csv")

