from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion


def get_feature_configs():

    feature_configs = {

        "Word_1_2": FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True
                )
            )
        ]),

        "Word_1_3": FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    lowercase=True,
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.98,
                    sublinear_tf=True,
                    strip_accents="unicode"
                )
            )
        ]),

        "Char_3_5": FeatureUnion([
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    sublinear_tf=True
                )
            )
        ]),

        "Word_Char": FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    lowercase=True,
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.98,
                    sublinear_tf=True,
                    strip_accents="unicode"
                )
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    sublinear_tf=True
                )
            )
        ])
    }

    return feature_configs