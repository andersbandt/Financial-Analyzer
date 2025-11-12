
# import needed modules
from analysis.data_recall import transaction_recall as transr
from categories import categories_helper as cath
from account import account_helper as acch
from tools import date_helper as dateh


# import
import pandas as pd
import re
from scipy import sparse
from scipy.sparse import hstack, csr_matrix

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


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
    #data["IsMonthStart"] = data["DateTime"].dt.is_month_start.astype(int)
    #data["IsMonthEnd"] = data["DateTime"].dt.is_month_end.astype(int)
    return data

# create category ancestry chain for addition to vectors
def add_category_features(data: pd.DataFrame):
    # do frequency encoding
    freq_map = data["category_id"].value_counts(normalize=True)
    # Map back to original DataFrame
    data["CategoryIDFreq"] = data["category_id"].map(freq_map)

    # add paths back to parent
    # cat_paths = []
    # for cid in data["category_id"]:
    #     if pd.isna(cid):
    #         cat_paths.append(["Unknown"])
    #     else:
    #         cat_paths.append(cath.get_category_parent_path_upwards(cid))
    # # Join ancestry chain into a string for encoding later
    # data["CategoryPath"] = [" > ".join(map(str, path)) for path in cat_paths]
    return data


def process_feature_text(data):
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
        return text

    data["DescriptionClean"] = data["description"].apply(preprocess_text)
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),  # unigrams + bigrams
        max_features=1000
    )
    X_text = tfidf.fit_transform(data["DescriptionClean"])
    return X_text


def encode_categorical_features(data: pd.DataFrame):
    cat_features = ["CategoryPath"]
    enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded = enc.fit_transform(data[cat_features])
    encoded_df = pd.DataFrame(encoded, columns=enc.get_feature_names_out(cat_features))
    data = pd.concat([data.drop(columns=cat_features), encoded_df], axis=1)
    return data, enc


def prepare_training_data(transactions, add_text=True):
    print("... converting transaction to dateframe")
    data = transactions_to_dataframe(transactions)
    print("... adding date features")
    data = add_date_features(data)

    print("... adding special category features")
    data = add_category_features(data)

    print("... adding vectorized text descriptions")
    data_text = process_feature_text(data)

    #print("... performing encoding")
    #data, enc = encode_categorical_features(data)

    print("... creating output values y")
    y = data["category_id"].copy()

    # drop not needed columns and concatenate our values
    data = data.drop(columns=["account_id", "date", "DateTime", "category_id", "description", "DescriptionClean"])

    if add_text:
        data = hstack([
            sparse.csr_matrix(data),
            data_text  # already sparse
        ])
    enc = None
    return data, enc, y


############################################
###    MAIN FUNCTION   #####################
############################################
### STEP 1: LOAD DATA
transactions = transr.recall_transaction_data()
print(f"Loading {len(transactions)} transactions")


### STEP 2: PREPARE TRAINING DATA
X, encoder, y = prepare_training_data(transactions, add_text=True)

# Check type and handle accordingly
if isinstance(X, pd.DataFrame):
    print("Data type: Pandas DataFrame")
    print(X.dtypes)
    print(X.head(10))
elif isinstance(X, csr_matrix):
    print("Data type: SciPy CSR sparse matrix")
    print(f"Sparsity: {X.nnz / (X.shape[0] * X.shape[1]):.4f}")
    print("Preview (dense subset):")
    print(X[:10].toarray())
else:
    print(f"Unknown type: {type(X)}")
    try:
        print(X[:10])
    except Exception as e:
        print("Preview unavailable:", e)


### STEP 3: CREATE TEST/TRAIN DATA
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


### STEP 4: SCALE FEATURES
scaler = StandardScaler(with_mean=False)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


### STEP 5: TRAIN CLASSIFIER
# TODO: maybe do a graph of iterations and accuracy --> interesting relationship going on where if I increase my accuracy plummets
model = LogisticRegression(multi_class="multinomial", max_iter=250)
model.fit(X_train_scaled, y_train)


### STEP 6: EVALUATE PERFORMANCE
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))








