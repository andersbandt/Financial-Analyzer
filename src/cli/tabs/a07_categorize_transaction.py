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
        uncategorized_statement.categorize_manual()
        uncategorized_statement.update_statement()

        return True


    def a03_update_transaction_category(self):
        print(" ... updating transaction categories ...")

        # STEP 1: Get transactions to update
        search_options = ["SEARCH", "MANUAL"]
        search_type = clih.prompt_num_options("How do you want to procure sql key to update?: ",
                                              search_options)
        if search_type is False:
            print("Ok, quitting transaction update\n")
            return False

        found_sql_key = []
        if search_type == 1:
            found_transactions = transh.search_trans()
            if found_transactions is False:
                print("... and quitting update transactions category too !")
                return False

            # Add all found transactions to the list
            if len(found_transactions) >= 1:
                for transaction in found_transactions:
                    found_sql_key.append(transaction.sql_key)
            else:
                print("No transactions found from search. Quitting.")
                return False

        elif search_type == 2:
            sql_key = clih.spinput("Please enter sql key to update: ", inp_type="int")
            if sql_key is False:
                print("Ok, quitting transaction update\n")
                return False
            found_sql_key.append(sql_key)

        # STEP 2: Show transactions found and allow removal if from search
        print(f"\n=== Found {len(found_sql_key)} transaction(s) ===")
        for id_key in found_sql_key:
            transaction = transr.get_transaction(id_key)
            transaction.print_trans(include_sql_key=True)

        if search_type == 1:
            print("\n--- You can now remove transactions you don't want to update ---")
            status = True
            while status:
                sql_to_remove = clih.spinput(
                    "\nEnter sql key of transaction to REMOVE from update list (or quit to continue): ",
                    "int")
                if sql_to_remove is False:
                    status = False
                else:
                    if sql_to_remove in found_sql_key:
                        found_sql_key.remove(sql_to_remove)
                        print(f"Removed sql_key={sql_to_remove}")
                        # reprint updated list
                        print(f"\n=== {len(found_sql_key)} transaction(s) remaining ===")
                        for id_key in found_sql_key:
                            transaction = transr.get_transaction(id_key)
                            transaction.print_trans(include_sql_key=True)
                    else:
                        print(f"sql_key={sql_to_remove} not in list!")

        if len(found_sql_key) == 0:
            print("No transactions left to update. Quitting")
            return False

        # STEP 3: Show final list and get new category
        print(f"\n=== Final list: {len(found_sql_key)} transaction(s) will be updated ===")
        for id_key in found_sql_key:
            transaction = transr.get_transaction(id_key)
            transaction.print_trans(include_sql_key=True)

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
        print(f"SQL keys: {found_sql_key}")

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




