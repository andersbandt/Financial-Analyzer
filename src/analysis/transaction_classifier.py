


# import needed modules
import re
import pandas as pd
import numpy as np


# import ML modules (sklearn)
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder, FunctionTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression



class TextCleaner(BaseEstimator, TransformerMixin):
    """
    Cleans text data by converting to lowercase and removing punctuation.
    Compatible with sklearn pipelines and ColumnTransformer.
    """

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Transform input text data.

        Parameters:
        -----------
        X : array-like, Series, or DataFrame
            Input data to clean

        Returns:
        --------
        numpy.ndarray : Cleaned text as 2D array (required for sklearn pipelines)
        """

        def preprocess_text(text):
            if text is None or pd.isna(text):
                return ""
            text = str(text).lower()
            text = re.sub(r"[^\w\s]", "", text)
            text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
            return text

        # Handle different input types
        if isinstance(X, pd.DataFrame):
            # If DataFrame with single column, extract it
            if X.shape[1] == 1:
                X_clean = X.iloc[:, 0].apply(preprocess_text)
            else:
                raise ValueError(f"Expected single column, got {X.shape[1]} columns")
        elif isinstance(X, pd.Series):
            X_clean = X.apply(preprocess_text)
        else:
            # Handle numpy array or list
            X_clean = pd.Series(X).apply(preprocess_text)

        # Return as 1D numpy array of strings
        # TfidfVectorizer expects 1D array-like of strings
        return X_clean.values


class FinancialTextCleaner:
    def __call__(self, text):
        if text is None:
            return ""
        text = text.lower()
        # text = re.sub(r"[^a-z0-9\s]", " ", text)  # keep numbers, drop punctuation
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text


class TransactionClassifier:
    def __init__(self, max_iter=1000, class_weight='balanced'):
        self.cleaner = FinancialTextCleaner()
        self.class_weight = class_weight

        self.preprocess = ColumnTransformer(

            transformers=[
                ("text", Pipeline([
                    ("clean", FunctionTransformer(
                        self._clean_text_batch, validate=False)),
                    ("tfidf", TfidfVectorizer(ngram_range=(1, 3), max_features=3000))
                ]), "description"),
                # Using more features including Month for seasonal patterns, IsWeekend for weekday/weekend differences
                ("num", StandardScaler(with_mean=False), ["value", "AccountType", "Month", "Day", "DayOfWeek", "IsWeekend", "AmountBucket"])
            ]
        )

        self.model = Pipeline([
            ("prep", self.preprocess),
            ("clf", LogisticRegression(
                multi_class="multinomial",
                max_iter=max_iter,
                class_weight=self.class_weight  # FIX: Use the parameter instead of None
            ))
        ])

        self.is_trained = False

    def _clean_text_batch(self, x):
        """Helper method for cleaning text in batches. Must be a regular method for pickling."""
        return [self.cleaner(t) for t in x]

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        return self.model.predict(X)

    def save(self, path="analysis/model.joblib"):
        import joblib
        joblib.dump(self.model, path)

    @staticmethod
    def load(path="analysis/model.joblib"):
        import joblib
        clf = TransactionClassifier()
        clf.model = joblib.load(path)
        clf.is_trained = True
        return clf