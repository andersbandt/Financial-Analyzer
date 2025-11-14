
# import needed modules
from analysis.data_recall import transaction_recall as transr
from categories import categories_helper as cath
from account import account_helper as acch
from tools import date_helper as dateh
from statement_types import Transaction


# import
import pandas as pd
import re
import matplotlib.pyplot as plt

# import
from scipy import sparse
from scipy.sparse import hstack, csr_matrix

from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score


# TODO: some printout of all the categories (by name) and their scores would be nice. Bonus points to order them in score

# TODO: need to play with the text cleaning more, I don't think it's helping anything
# TODO: also need to play with the text vectorizer more

# TODO: do an audit of my training and test data collections

# TODO: need to do some thinking on how I can train with categorical info but not need to include it in the final model ... like parent category or paths

# TODO: refactor the `prepare_transactions` to not need to generate y ... don't need y when I'm using this thing normally

# TODO:



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


class TransactionClassifier:
    def __init__(self, max_iter=1000, class_weight='balanced'):
        self.preprocess = ColumnTransformer(
            transformers=[
                ("text", Pipeline([
                    # ("clean", TextCleaner()),
                    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=2000))
                ]), "description"),
                # ("num", StandardScaler(with_mean=False), ["value", "AccountType", "Year", "Month", "Day", "DayOfWeek", "IsMonthStart", "IsMonthEnd"])
                ("num", StandardScaler(with_mean=False), ["value", "AccountType", "Day", "DayOfWeek"])
            ]
        )

        self.model = Pipeline([
            ("prep", self.preprocess),
            ("clf", LogisticRegression(
                multi_class="multinomial",
                max_iter=max_iter,
                class_weight=class_weight
            ))
        ])

        self.is_trained = False

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        return self.model.predict(X)

    def save(self, path="model.joblib"):
        import joblib
        joblib.dump(self.model, path)

    @staticmethod
    def load(path="model.joblib"):
        import joblib
        clf = TransactionClassifier()
        clf.model = joblib.load(path)
        clf.is_trained = True
        return clf


### STEP 1: LOAD IN TRAINING DATA
def prepare_transactions(transactions):
    data = pd.DataFrame([{
        "account_id": t.account_id,
        "date": t.date,
        "value": t.value,
        "description": t.description,
        "category_id": t.category_id
    } for t in transactions])

    # do some really quick data conversions
    data["DateTime"] = pd.to_datetime(data["date"], format="%Y-%m-%d", errors="coerce")
    data["AccountType"] = data["account_id"].apply(acch.get_account_type_by_id)
    data["Year"] = data["DateTime"].dt.year
    data["Month"] = data["DateTime"].dt.month
    data["Day"] = data["DateTime"].dt.day
    data["DayOfWeek"] = data["DateTime"].dt.dayofweek
    data["IsMonthStart"] = data["DateTime"].dt.is_month_start.astype(int)
    data["IsMonthEnd"] = data["DateTime"].dt.is_month_end.astype(int)

    y = data["category_id"]
    # y = LabelEncoder().fit_transform(data["category_id"])

    # drop not needed columns and concatenate our values
    data = data.drop(columns=["account_id", "date", "DateTime", "category_id", "CategoryTop", "DescriptionClean"],
                     errors="ignore")
    return data, y


### ANOTHER EVALUATIN YET AGAIN
def graph_accuracy(iters, X_trn, X_tst, y_trn, y_tst):
    scores = []

    for i in iters:
        model = TransactionClassifier(max_iter=i)

        model.train(X_trn, y_trn)
        yp = model.predict(X_tst)

        acc = accuracy_score(y_tst, yp)
        scores.append(acc)

        print(f"max_iter={i}, accuracy={acc:.3f}")

    plt.plot(iters, scores, marker='o')
    plt.xlabel("Max Iterations")
    plt.ylabel("Accuracy")
    plt.title("Logistic Regression Accuracy vs. Iterations")
    plt.grid(True)
    plt.show()


############################################
###    MAIN FUNCTION   #####################
############################################
### STEP 1: LOAD DATA
transactions = transr.recall_transaction_data()
print(f"Loading {len(transactions)} transactions")


### STEP 2: PREPARE TRAINING DATA
X, y = prepare_transactions(transactions)

# Check type and handle accordingly
if isinstance(X, pd.DataFrame):
    print("Data type: Pandas DataFrame")
    print(X.dtypes)
    print(X.head(5))
elif isinstance(X, csr_matrix):
    print("Data type: SciPy CSR sparse matrix")
    print(f"Sparsity: {X.nnz / (X.shape[0] * X.shape[1]):.4f}")
    print("Preview (dense subset):")
    print(X[:5].toarray())
else:
    print(f"Unknown type: {type(X)}")
    try:
        print(X[:5])
    except Exception as e:
        print("Preview unavailable:", e)
print("TRAINING DATA INFO ABOVE !!!")


### STEP 3: CREATE TEST/TRAIN DATA
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


### STEP 5: TRAIN CLASSIFIER
print("... training model")
tc = TransactionClassifier(max_iter=5000)
tc.train(X_train, y_train)
# tc.save("model.joblib")


### STEP 6: EVALUATE PERFORMANCE
y_pred = tc.predict(X_test)
print(classification_report(y_test, y_pred))

# graph_accuracy([100, 500, 1000, 5000, 7500, 10000, 30000],
#                X_train,
#                X_test,
#                y_train,
#                y_test)






### actually unused code here

# def encode_categorical_features(data: pd.DataFrame):
#     cat_features = ["CategoryPath"]
#     enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
#     encoded = enc.fit_transform(data[cat_features])
#     encoded_df = pd.DataFrame(encoded, columns=enc.get_feature_names_out(cat_features))
#     data = pd.concat([data.drop(columns=cat_features), encoded_df], axis=1)
#     return data, enc

# create category ancestry chain for addition to vectors
# def add_category_features(data: pd.DataFrame):
    # do frequency encoding
    # freq_map = data["category_id"].value_counts(normalize=True)
    # # Map back to original DataFrame
    # data["CategoryIDFreq"] = data["category_id"].map(freq_map)

    # data["CategoryTop"] = data["category_id"].apply(
    #     lambda x: cath.get_category_parent_path_upwards(x)[-1] if cath.get_category_parent_path_upwards(x) else 0
    # )

    # add paths back to parent
    # cat_paths = []
    # for cid in data["category_id"]:
    #     if pd.isna(cid):
    #         cat_paths.append(["Unknown"])
    #     else:
    #         cat_paths.append(cath.get_category_parent_path_upwards(cid))
    # # Join ancestry chain into a string for encoding later
    # data["CategoryPath"] = [" > ".join(map(str, path)) for path in cat_paths]
    # return data