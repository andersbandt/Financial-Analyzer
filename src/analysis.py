
# import needed modules
from analysis.data_recall import transaction_recall as transr
from categories import categories_helper as cath
from account import account_helper as acch
from tools import date_helper as dateh
from statement_types import Transaction


# import
import pandas as pd
import re
from scipy import sparse
from scipy.sparse import hstack, csr_matrix

from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline


class TransactionClassifier:
    def __init__(self, max_iter=1000, class_weight='balanced'):
        self.preprocess = ColumnTransformer(
            transformers=[
                ("text", TfidfVectorizer(), "description"),
                ("num", StandardScaler(with_mean=False), ["value", "Year", "Month", "Day", "DayOfWeek"])
            ],
            remainder="drop"
        )

        self.model = Pipeline([
            ("prep", self.preprocess),
            ("clf", LogisticRegression(
                multi_class="multinomial",
                max_iter=max_iter,
                class_weight=class_weight
            ))
        ])

        self.class_weight = class_weight
        self.is_trained = False

    def train(self, X_text, y):
        self.model.fit(X_text, y)
        self.is_trained = True

    def predict(self, X_text):
        if not self.is_trained:
            raise RuntimeError("Model not trained.")
        return self.model.predict(X_text)

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
def transactions_to_dataframe(transactions):
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
    return data


### STEP 2: CREATE FEATURE VECTORS
# add temporal (date) features
def add_date_features(data: pd.DataFrame):
    data["Year"] = data["DateTime"].dt.year
    data["Month"] = data["DateTime"].dt.month
    data["Day"] = data["DateTime"].dt.day
    data["DayOfWeek"] = data["DateTime"].dt.dayofweek
    data["IsMonthStart"] = data["DateTime"].dt.is_month_start.astype(int)
    data["IsMonthEnd"] = data["DateTime"].dt.is_month_end.astype(int)
    return data


def format_transactions(data):
    print("... adding date features")
    data = add_date_features(data)

    # drop not needed columns and concatenate our values
    data = data.drop(columns=["account_id", "date", "DateTime", "category_id", "CategoryTop", "DescriptionClean"],
                     errors="ignore")

    # data = hstack([
    #     sparse.csr_matrix(data),
    #     data_text  # already sparse
    # ])

    enc = None
    return data, enc


def prepare_training_data(td):
    print("... converting transaction to dateframe")
    data = transactions_to_dataframe(td)

    print("... creating output values y")
    y = data["category_id"]
    # y = LabelEncoder().fit_transform(data["CategoryTop"])

    print("... formatting Transaction array into proper format")
    data, enc = format_transactions(data)

    return data, enc, y




# EVALUATION
def eval_model():
    model = make_pipeline(
        StandardScaler(with_mean=False),
        LogisticRegression(max_iter=1000, class_weight='balanced', multi_class='multinomial')
    )

    scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
    print(scores.mean())

### ANOTHER EVALUATIN YET AGAIN
def graph_accuracy(model, iters, X_test, X_train, y_test, y_train):
    scores = []

    for i in iters:
        model = TransactionClassifier(max_iter=i)

        model.train(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
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
X, encoder, y = prepare_training_data(transactions)

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
tc = TransactionClassifier(max_iter=10)
tc.train(X_train, y_train)
# tc.save("model.joblib")


### STEP 6: EVALUATE PERFORMANCE
y_pred = tc.predict(X_test)
print(classification_report(y_test, y_pred))

graph_accuracy(tc,
               [100, 500, 1000, 5000, 7500, 10000, 20000, 30000],
               X_train,
               X_test,
               y_train,
               y_test)


# transactions = transr.recall_transaction_month_bin(2024, 3)
# X, encoder, y = prepare_training_data(transactions)
#
# y_pred = model.predict(X)
# category_pred = cath.category_id_to_name(y_pred)

# print("Yo fucker you predicted below")
# for i in range(0, len(category_pred)):
#     transactions[i].print_trans()
#     print(category_pred[i])


### actually unused code here

# def process_feature_text(data):
#     def preprocess_text(text):
#         text = text.lower()
#         text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
#         return text
#
#     data["DescriptionClean"] = data["description"].apply(preprocess_text)
#     tfidf = TfidfVectorizer(
#         ngram_range=(1, 2),  # unigrams + bigrams
#         max_features=1000
#     )
#     X_text = tfidf.fit_transform(data["DescriptionClean"])
#     return X_text


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