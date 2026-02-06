
# import needed modules
from analysis.data_recall import transaction_recall as transr
from categories import categories_helper as cath
from account import account_helper as acch
from tools import date_helper as dateh
from statement_types import Transaction
from analysis import transaction_classifier


# import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# import
from scipy import sparse
from scipy.sparse import hstack, csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score



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

    # Add new engineered features
    data["IsWeekend"] = (data["DayOfWeek"] >= 5).astype(int)  # Saturday=5, Sunday=6

    # Bucket transaction amounts (helps model generalize better)
    # Fill any NaN amounts with 0 before bucketing
    amount_abs = data["value"].abs().fillna(0)
    data["AmountBucket"] = pd.cut(
        amount_abs,
        bins=[0, 10, 50, 100, 500, float('inf')],
        labels=[0, 1, 2, 3, 4]
    ).cat.codes

    y = data["category_id"]

    # Drop only the columns we actually don't need (removed phantom columns)
    data = data.drop(columns=["account_id", "date", "DateTime", "category_id", "Year", "IsMonthStart", "IsMonthEnd"],
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
print(f"\n{'='*80}")
print(f"Loading {len(transactions)} transactions")
print(f"{'='*80}\n")


### STEP 2: PREPARE TRAINING DATA
X, y = prepare_transactions(transactions)

# Check type and handle accordingly
if isinstance(X, pd.DataFrame):
    print("Data type: Pandas DataFrame")
    print(X.dtypes)
    print(f"\nData shape: {X.shape}")
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


### CLASS DISTRIBUTION ANALYSIS
print(f"\n{'='*80}")
print("CLASS DISTRIBUTION ANALYSIS")
print(f"{'='*80}")
class_counts = y.value_counts()
print(f"\nTotal categories: {len(class_counts)}")
print(f"\nTop 10 most common categories:")
for cat_id, count in class_counts.head(10).items():
    cat_name = cath.category_id_to_name(cat_id)
    pct = (count / len(y)) * 100
    print(f"  {cat_name:30s} - {count:5d} transactions ({pct:5.2f}%)")

print(f"\nBottom 5 least common categories:")
for cat_id, count in class_counts.tail(5).items():
    cat_name = cath.category_id_to_name(cat_id)
    pct = (count / len(y)) * 100
    print(f"  {cat_name:30s} - {count:5d} transactions ({pct:5.2f}%)")

# Warn about severe imbalance
min_samples = class_counts.min()
if min_samples < 10:
    print(f"\n⚠️  WARNING: Some categories have very few samples (min={min_samples})")
    print("   Consider combining rare categories or collecting more data.")


### STEP 3: CREATE TEST/TRAIN DATA
# Note: Not using stratify because some categories have only 1 sample
# For better results, consider combining rare categories into "OTHER"
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)
print(f"\n{'='*80}")
print(f"Train set: {len(X_train)} transactions")
print(f"Test set:  {len(X_test)} transactions")
print(f"{'='*80}\n")


### STEP 4: TRAIN CLASSIFIER WITH CROSS-VALIDATION
print("Training model with cross-validation...")
tc = transaction_classifier.TransactionClassifier(max_iter=2000, class_weight='balanced')

# Perform 5-fold cross-validation on training data
cv_scores = cross_val_score(tc.model, X_train, y_train, cv=5, scoring='accuracy')
print(f"\n5-Fold Cross-Validation Scores: {cv_scores}")
print(f"Mean CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# Train on full training set
print("\nTraining final model on full training set...")
tc.train(X_train, y_train)
print("✓ Training complete!\n")


### STEP 5: EVALUATE PERFORMANCE
print(f"{'='*80}")
print("TEST SET EVALUATION")
print(f"{'='*80}\n")

y_pred = tc.predict(X_test)
test_accuracy = accuracy_score(y_test, y_pred)
print(f"Test Set Accuracy: {test_accuracy:.3f}\n")

unique_labels = np.unique(np.concatenate([y_test, y_pred]))
category_names = [cath.category_id_to_name(lbl) for lbl in unique_labels]
print(classification_report(y_test, y_pred, labels=unique_labels, target_names=category_names, zero_division=0))


### STEP 6: ANALYZE ERRORS
print(f"\n{'='*80}")
print("ERROR ANALYSIS - Misclassified Transactions")
print(f"{'='*80}\n")

misclassified_mask = y_test != y_pred
misclassified_indices = y_test[misclassified_mask].index

if len(misclassified_indices) > 0:
    print(f"Total misclassifications: {len(misclassified_indices)}")
    print("\nSample of misclassified transactions (first 10):\n")

    for idx in list(misclassified_indices)[:10]:
        true_cat = cath.category_id_to_name(y_test.loc[idx])
        pred_cat = cath.category_id_to_name(y_pred[y_test.index.get_loc(idx)])
        desc = X.loc[idx, 'description']
        amount = X.loc[idx, 'value']
        print(f"  Description: {desc[:50]:50s}")
        print(f"  Amount: ${amount:8.2f}")
        print(f"  True:      {true_cat}")
        print(f"  Predicted: {pred_cat}")
        print()
else:
    print("No misclassifications! Perfect accuracy!")



### STEP 7: OPTIONAL - HYPERPARAMETER TUNING
# Uncomment to experiment with different iteration counts
# print("\n" + "="*80)
# print("HYPERPARAMETER TUNING")
# print("="*80 + "\n")
# graph_accuracy([100, 500, 1000, 2000, 5000, 10000],
#                X_train,
#                X_test,
#                y_train,
#                y_test)


### STEP 8: SAVE MODEL
print(f"\n{'='*80}")
res = input("Do you want to save this classifier? (y/n): ").strip().lower()
if res == "y":
    print("✓ Saving classifier to analysis/model.joblib")
    tc.save()
    print("✓ Model saved successfully!")
else:
    print("✗ Model NOT saved")
print(f"{'='*80}\n")



