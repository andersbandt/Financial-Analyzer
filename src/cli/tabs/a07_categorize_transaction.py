"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined modules
import categories.categories_helper as cath
from categories import categories_helper
from statement_types import Transaction
from statement_types import Ledger
from analysis.data_recall import transaction_recall as transr
from analysis import transaction_helper as transh
import db.helpers as dbh


class TabTransCategorize(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [
            Action("Print uncategorized", self.a01_print_uncategorized),
            Action("Categorize uncategorized", self.a02_categorize_NA),
            Action("Update categories", self.a03_update_transaction_category)
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_print_uncategorized(self):
        ledger_data = dbh.transactions.get_uncategorized_transactions()

        transactions = []
        for data in ledger_data:
            transactions.append(
                Transaction.Transaction(
                    data[1], data[2], data[3], data[4], data[5], sql_key=data[0], note=data[6]
                )
            )

        uncategorized_statement = Ledger.Ledger("Uncategorized Transactions!", transactions=transactions)
        uncategorized_statement.print_statement()


    def a02_categorize_NA(self):
        print("... categorizing uncategorized transaction ...")
        ledger_data = dbh.transactions.get_uncategorized_transactions()

        transactions = []
        for data in ledger_data:
            transactions.append(
                Transaction.Transaction(
                    data[1], data[2], data[3], data[4], data[5], sql_key=data[0], note=data[6]
                )
            )

        uncategorized_statement = Ledger.Ledger("Uncategorized Transactions!", transactions=transactions)
        uncategorized_statement.categorizeLedgerAutomatic(categories_helper.load_categories())
        uncategorized_statement.categorize_manual()  # return value intentionally ignored here
        uncategorized_statement.update_statement()

        return True


    def a03_update_transaction_category(self):
        print(" ... updating transaction categories ...")

        def print_transactions_table(sql_keys):
            rows = []
            for key in sql_keys:
                t = transr.get_transaction(key)
                cat_name = cath.category_id_to_name(t.category_id) if t.category_id else "NA"
                rows.append([t.sql_key, t.date, t.value, t.description, cat_name])
            clip.print_variable_table(
                ["SQL Key", "Date", "Amount", "Description", "Category"],
                rows,
                max_width=50,
                max_width_column="Description",
            )

        # STEP 1: Get transactions to update
        search_options = ["SEARCH", "MANUAL", "PICK FROM CATEGORY"]
        search_type = clih.prompt_num_options("How do you want to find transactions to update?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction update\n")
            return False

        found_sql_key = []

        if search_type == 1:  # SEARCH — find all matches, then drop unwanted ones
            found_transactions = transh.search_trans()
            if found_transactions is False:
                print("... and quitting update transactions category too !")
                return False
            if len(found_transactions) >= 1:
                for transaction in found_transactions:
                    found_sql_key.append(transaction.sql_key)
            else:
                print("No transactions found from search. Quitting.")
                return False

        elif search_type == 2:  # MANUAL — enter individual sql keys
            print("Enter sql keys one at a time. Quit when done.")
            while True:
                sql_key = clih.spinput("Please enter sql key to add (or quit to finish): ", inp_type="int")
                if sql_key is False:
                    break
                found_sql_key.append(sql_key)
                print(f"Added sql_key={sql_key}. Total so far: {len(found_sql_key)}")
            if not found_sql_key:
                print("No sql keys entered. Quitting.")
                return False

        elif search_type == 3:  # PICK FROM CATEGORY — browse category, pick specific transactions
            category_id = clih.category_prompt_all("Which category to browse?", False)
            if category_id is False:
                print("Ok, quitting transaction update\n")
                return False
            all_transactions = transr.recall_transaction_category(category_id)
            if not all_transactions:
                print("No transactions found for that category. Quitting.")
                return False
            all_sql_keys = [t.sql_key for t in all_transactions]
            print(f"\n=== {len(all_sql_keys)} transaction(s) in category ===")
            print_transactions_table(all_sql_keys)

            print("\nEnter sql keys to ADD to update list. Quit when done.")
            while True:
                sql_key = clih.spinput("Enter sql key to add (or quit to finish): ", inp_type="int")
                if sql_key is False:
                    break
                if sql_key in all_sql_keys:
                    found_sql_key.append(sql_key)
                    print(f"Added sql_key={sql_key}. Total so far: {len(found_sql_key)}")
                else:
                    print(f"sql_key={sql_key} not found in that category!")
            if not found_sql_key:
                print("No transactions selected. Quitting.")
                return False

        # STEP 2: Show transactions found; SEARCH mode allows dropping unwanted ones
        print(f"\n=== Found {len(found_sql_key)} transaction(s) ===")
        print_transactions_table(found_sql_key)

        if search_type == 1:
            print("\n--- Remove any transactions you don't want to update ---")
            while True:
                sql_to_remove = clih.spinput(
                    "\nEnter sql key to REMOVE from list (or quit to continue): ", "int")
                if sql_to_remove is False:
                    break
                if sql_to_remove in found_sql_key:
                    found_sql_key.remove(sql_to_remove)
                    print(f"Removed sql_key={sql_to_remove}")
                    print(f"\n=== {len(found_sql_key)} transaction(s) remaining ===")
                    print_transactions_table(found_sql_key)
                else:
                    print(f"sql_key={sql_to_remove} not in list!")

        if len(found_sql_key) == 0:
            print("No transactions left to update. Quitting")
            return False

        # STEP 3: Show final list and get new category
        print(f"\n=== Final list: {len(found_sql_key)} transaction(s) will be updated ===")
        print_transactions_table(found_sql_key)

        new_category_id = clih.category_prompt_all(
            "\nWhat is the new category for these transactions?",
            False)

        if new_category_id is False:
            print("Ok, quitting transaction category update")
            return False

        # STEP 4: Final confirmation
        new_category_name = cath.category_id_to_name(new_category_id)
        print(f"\n=== CONFIRMATION ===")
        print(f"About to update {len(found_sql_key)} transaction(s) to category: {new_category_name}")

        confirm = clih.promptYesNo("Are you sure you want to update these transactions?")
        if not confirm:
            print("Ok, cancelling transaction category update")
            return False

        # STEP 5: Update transactions
        for key in found_sql_key:
            dbh.transactions.update_transaction_category_k(key, new_category_id)

        print(f"\n✓ Successfully updated {len(found_sql_key)} transaction(s) to category: {new_category_name}")
        return True

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################




