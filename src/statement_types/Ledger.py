"""
Class: Ledger

Ledger is a basic class simply for holding transactions together in a ledger

"""

# import user defined modules
import categories.categories_helper as cath
import db.helpers as dbh
import cli.cli_helper as clih
import cli.cli_printer as clip
import analysis.transaction_helper as transh


class Ledger:
    def __init__(self, title, transactions=None):
        # set ledger variables
        self.title = title

        # init ledger data variables
        if transactions is None:
            self.transactions = []
        else:
            self.transactions = transactions

    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # set_statement_data: sets the transaction data
    def set_statement_data(self, transactions):
        self.transactions = transactions

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    def get_number_uncategorized(self):
        num = 0
        for transaction in self.transactions:
            if transaction.category_id is None or transaction.category_id == 0:
                num += 1
        return num

    def getUncategorizedTrans(self):
        uncategorized_transaction = []
        for transaction in self.transactions:
            if not transaction.get_cat_status():
                uncategorized_transaction.append(transaction)
        return uncategorized_transaction

    # categorizeStatementAutomatic: adds a category label to each statement array based predefined
    def categorizeLedgerAutomatic(self, categories):
        # PERFORM VARIABLE CHECKS
        if len(categories) == 0:
            raise Exception("Loaded categories length is 0")

        if self.transactions is None:
            print("Can't categorize Ledger: ", self.title)
            print("No transactions loaded.")
            return

        # iterate through transactions and categorize them
        for transaction in self.transactions:
            transaction.categorizeTransactionAutomatic(categories)
        return

    def categorize_manual(self):
        i = 0
        num_to_categorize = self.get_number_uncategorized()

        # prompt user for mode of categorization
        # cat_mode = clih.spinput("What num mode do you want to do categorization?\n"
                                # "mode 1=tree style\n"
                                # "mode 2=all category\n"
                                # " 1-2: ", inp_type="int")
        cat_mode = 2

        for transaction in self.getUncategorizedTrans():
            # prompt user for category information
            print("\n")
            category_id = transh.get_trans_category_cli(transaction, mode=cat_mode)

            if category_id == -1:
                print("Received bad category ID\n"
                      "Suspending statement manual categorize")
                res = clih.promptYesNo("Do you want to stop categorization?")
                if res:
                    return False
            else:
                # set transaction
                transaction.setCategory(category_id)
                i += 1
                print("Transactions left:", num_to_categorize - i)
        return True

    def categorize_ml(self):
        """
        Categorize uncategorized transactions using the trained ML model.
        """
        import pandas as pd
        from analysis import transaction_classifier
        from account import account_helper as acch

        # Get uncategorized transactions
        uncategorized = self.getUncategorizedTrans()
        if len(uncategorized) == 0:
            print("No uncategorized transactions to classify.")
            return

        print(f"Classifying {len(uncategorized)} transactions using ML model...")

        # Load the trained model
        tc = transaction_classifier.TransactionClassifier.load()

        # Convert transactions to DataFrame with same format as training data
        data = pd.DataFrame([{
            "description": t.description,
            "value": t.value,
            "account_id": t.account_id,
            "date": t.date
        } for t in uncategorized])

        # Create the same features used during training
        data["DateTime"] = pd.to_datetime(data["date"], format="%Y-%m-%d", errors="coerce")
        data["AccountType"] = data["account_id"].apply(acch.get_account_type_by_id)
        data["Day"] = data["DateTime"].dt.day
        data["DayOfWeek"] = data["DateTime"].dt.dayofweek

        # Drop columns not needed for prediction
        X = data.drop(columns=["account_id", "date", "DateTime"])

        # Predict categories
        predicted_categories = tc.predict(X)

        # Update transactions with predicted categories
        for transaction, category_id in zip(uncategorized, predicted_categories):
            transaction.setCategory(category_id)
            if transaction.note:
                transaction.note = transaction.note + ";ml_classified"
            else:
                transaction.note = "ml_classified"

        print(f"Successfully classified {len(uncategorized)} transactions.")
        return True

    ##############################################################################
    ####      ORDERING FUNCTIONS    ##############################################
    ##############################################################################

    # sort:trans_asc: sorts the transactions by amount ascending (highest to lowest)
    def sort_trans_asc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.value)
        self.transactions = sorted_trans

    # sort_trans_desc: sorts the transaction by amount descending (lowest to highest)
    def sort_trans_desc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.value, reverse=True)
        self.transactions = sorted_trans

    # sort_date_desc: end of transaction array will be most recent date
    def sort_date_desc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.date)
        self.transactions = sorted_trans

    # sort_date_asc: start of transaction array will be most recent date
    def sort_date_asc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.date, reverse=True)
        self.transactions = sorted_trans

    ##############################################################################
    ####      PRINTING FUNCTIONS    ##############################################
    ##############################################################################

    # printStatement: pretty prints a statement
    def print_statement(self, include_sql_key=False, method=1):
        if self.transactions is None:
            print("ERROR: can't print empty ledger!")
            return
        print("Ledger: ", self.title)

        # OLD METHOD: using print_transaction
        if method == 0:
            for transaction in self.transactions:
                transaction.print_trans(include_sql_key=include_sql_key)

        # NEW METHOD: using prettytable
        elif method == 1:
            if include_sql_key:
                headers = ["KEY", "DATE", "AMOUNT", "DESC", "CATEGORY", "ACCOUNT", "NOTE"]
            else:
                headers = ["DATE", "AMOUNT", "DESC", "CATEGORY", "ACCOUNT", "NOTE"]

            values = []
            for transaction in self.transactions:
                if include_sql_key:
                    cur_values = [
                        transaction.sql_key,
                        transaction.date,
                        transaction.value,
                        transaction.description,
                        cath.category_id_to_name(transaction.category_id),
                        dbh.account.get_account_name_from_id(transaction.account_id),
                        transaction.note
                    ]
                else:
                    cur_values = [
                        transaction.date,
                        transaction.value,
                        transaction.description,
                        cath.category_id_to_name(transaction.category_id),
                        dbh.account.get_account_name_from_id(transaction.account_id),
                        transaction.note
                    ]
                values.append(cur_values)
            clip.print_variable_table(headers, values, min_width=15, max_width=80, max_width_column="DESC")

        return True

    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # save_statement: saves a categorized statement as a csv
    def save_statement(self):
        # prompt user to verify desire to update ledger data
        print("Attempting to save Ledger...")
        response = clih.promptYesNo("Are you sure you want to save this Ledger ??")
        if response is False:
            print("Ok, not saving ledger data")
            return False
        else:
            error_status = 0
            for transaction in self.transactions:

                # INSERT TRANSACTION
                success = dbh.transactions.insert_transaction(transaction)
                if success == 0:
                    print("FAILED TO ADD TRANSACTION")
                    error_status = 1
                else:
                    pass
                    # print("Added transaction --> " + transaction.print_trans(False))

        # ERROR HANDLE
        if error_status == 1:
            print("\nError in ledger adding: At least 1 thing went wrong adding to a ledger")
            return False
        else:
            print("Saved Ledger")
        return True

    # delete_statement: deletes statement from master frame
    def delete_statement(self):
        print("Deleting ledger", self.title)

    def update_statement(self):
        print("Attempting to update Ledger...")
        error_flag = 0
        for transaction in self.transactions:
            success = dbh.transactions.update_transaction_category(transaction)
            if not success:
                error_flag = 1

        if error_flag:
            print("Uh oh, something went wrong updating ledger")

        print("Ledger updated")
