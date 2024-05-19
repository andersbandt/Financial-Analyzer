"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database


"""


# import user defined modules
from categories import categories_helper as cath
import cli.cli_helper as clih
from cli.tabs import SubMenu
from categories import categories_helper
from statement_types import Transaction
from statement_types import Ledger
import db.helpers as dbh


class TabTransCategorize(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_strings = ["Print uncategorized", "Categorize uncategorized"]
        action_funcs = [self.a01_print_uncategorized, self.a02_categorize_NA]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


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


# TODO: this whole function could use some tweaking
#   better workflow, pass in multiple SQL keys, printout of transaction before confirmation

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


    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################




