"""
TransactionClassifier: ML model for automatic transaction categorization.

Model design (chosen via cross-validated experiments on the real ledger, 2026-07):
- Text-only features. The numeric features (day, weekend, amount bucket, ...) used
  previously cost ~1.5pp of accuracy, so they were dropped.
- Two TF-IDF views of the description, combined:
    * char n-grams (2-5) on a "merchant-cleaned" string (digits/store numbers and
      punctuation stripped) -- robust to store #s, ref codes, and city/state suffixes
    * word n-grams (1-2) on a lightly cleaned string
- LogisticRegression, unweighted, C=5. class_weight='balanced' cost ~2pp overall
  accuracy by over-serving rare categories.
- predict_with_confidence() exposes predict_proba so callers can auto-apply only
  confident predictions (see Ledger.categorize_ml).

Measured on 4.2k labeled transactions / 59 classes (5-fold CV):
  ~80% raw accuracy; at confidence >= 0.8 the model auto-labels ~61% of
  transactions at ~98% accuracy.

IMPORTANT: prepare_features() is the single source of truth for feature prep.
Both the training script (src/analysis.py) and prediction (Ledger.categorize_ml)
must build their input frame through it so train/predict never drift apart.
"""

# import needed modules
import re
import pandas as pd

# import ML modules (sklearn)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def clean_text_basic(text):
    """Lowercase, strip punctuation, normalize whitespace."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_text_merchant(text):
    """Normalize a raw statement description down to its merchant-y core:
    drop *, #, any token containing a digit (store numbers, ref codes, dates),
    and all remaining non-letter characters."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text).lower()
    text = re.sub(r"[*#]", " ", text)
    text = re.sub(r"\b[a-z]*\d[\w]*\b", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class TransactionClassifier:
    def __init__(self, max_iter=2000, C=5.0):
        self.model = Pipeline([
            ("prep", ColumnTransformer(transformers=[
                ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                                         max_features=30000), "desc_merchant"),
                ("word", TfidfVectorizer(ngram_range=(1, 2),
                                         max_features=5000), "desc_clean"),
            ])),
            ("clf", LogisticRegression(max_iter=max_iter, C=C)),
        ])
        self.is_trained = False

    @staticmethod
    def prepare_features(items):
        """Build the model's feature DataFrame.

        items: list of Transaction objects, list of dicts with a 'description'
        key, or a DataFrame with a 'description' column.
        Returns a DataFrame with description / desc_clean / desc_merchant columns
        (extra columns like the raw description are kept for reporting; the
        ColumnTransformer only reads the columns it names).
        """
        if isinstance(items, pd.DataFrame):
            df = items.copy()
        else:
            df = pd.DataFrame([{
                "description": getattr(t, "description", None) if not isinstance(t, dict) else t.get("description")
            } for t in items])

        df["description"] = df["description"].fillna("")
        df["desc_clean"] = df["description"].map(clean_text_basic)
        df["desc_merchant"] = df["description"].map(clean_text_merchant)
        return df

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        return self.model.predict(X)

    def predict_with_confidence(self, X):
        """Returns (predictions, confidences) where confidence is the max
        class probability for each row. Use to gate automatic categorization."""
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        proba = self.model.predict_proba(X)
        preds = self.model.classes_[proba.argmax(axis=1)]
        return preds, proba.max(axis=1)

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
