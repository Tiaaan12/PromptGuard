from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB


def get_models():

    models = {

        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ),

        "Linear SVM": LinearSVC(
            class_weight="balanced",
            random_state=42
        ),

        "Naive Bayes": MultinomialNB()
    }

    return models