"""
Class: Transaction

Transaction represents a single transaction on any statement

"""


# import user defined modules
import categories.categories_helper as cath
import db.helpers as dbh
import cli.cli_helper as clih
import cli.cli_printer as clip


class Ledger:
    def __init__(self, title, transactions=None):
        # set ledger variables
        self.title = title

        # init ledger data variables
        self.transactions = transactions
        self.clicked_category = []  # holds all the user set categories

    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # set_statement_data: sets the transaction data
    def set_statement_data(self, transactions):
        self.transactions = transactions

    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # del_sel_trans: deletes selected transactions DIRECTLY from the SQL database
    def del_sel_trans(self):
        # print out what transactions we are deleting
        print("Deleting the transactions with the following sql keys: ")
        print(self.sel_trans)

        # go through selected Transactions and delete
        for sql_key in self.sel_trans:
            dbh.ledger.delete_transaction(sql_key)
        return

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # checkNA: checks if a statement contains any transactions with 'NA' as a category
    def checkNA(self):
        amount_NA = 0
        for transaction in self.transactions:
            if not transaction.get_cat_status():
                amount_NA += 1

        if amount_NA > 0:
            print("Analyzed statement, contains " + str(amount_NA) + " NA entries")
            return True
        else:
            return False


    def get_number_uncategorized(self):
        num = 0
        for transaction in self.transactions:
            if transaction.category_id == None or transaction.category_id == 0:
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
        print("\n categorizeLedgerAutomatic on:" + self.title)

        if len(categories) == 0:
            raise Exception("Loaded categories length is 0")

        if self.transactions is None:
            print("Can't category Ledger: ", self.title)
            print("No transactions loaded.")
            return

        for transaction in self.transactions:
            transaction.categorizeTransactionAutomatic(categories)
        return


    def categorize_manual(self):
        i = 0
        num_to_categorize = self.get_number_uncategorized()

        # prompt user for mode of categorization
        cat_mode = clih.spinput("What num mode do you want to do categorization?\n"
                                "mode 1=tree style\n"
                                "mode 2=all category\n"
                                " 1-2: ", inp_type="int")
        for transaction in self.getUncategorizedTrans():
            # prompt user for category information
            print("\n")
            category_id = clih.get_category_input(transaction, mode=cat_mode)

            if category_id == -1:
                print("Received bad category ID\n"
                      "Suspending statement manual categorize")
                res = clih.promptYesNo("Do you want to stop categorization?")
                if res:
                    return
            else:
                # set transaction
                transaction.setCategory(category_id)
                i += 1
                print("Transactions left:", num_to_categorize-i)


    ##############################################################################
    ####      ORDERING FUNCTIONS    ##############################################
    ##############################################################################
# TODO: my prettytable module also has sorting capability ... worthwhile to still have these functions?
    # sort:trans_asc: sorts the transactions by amount ascending (highest to lowest)
    def sort_trans_asc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount)
        self.transactions = sorted_trans

    # sort_trans_desc: sorts the transaction by amount descending (lowest to highest)
    def sort_trans_desc(self):
        sorted_trans = sorted(self.transactions, key=lambda t: t.amount, reverse=True)
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
    def print_statement(self, include_sql_key=False):
        if self.transactions is None:
            print("ERROR: can't print empty ledger!")
            return
        print("Ledger: ", self.title)

        # OLD METHOD: using print_transaction
        # for transaction in self.transactions:
        #     transaction.printTransaction(include_sql_key=include_sql_key)

        # NEW METHOD: using prettytable
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
                    transaction.amount,
                    transaction.description,
                    cath.category_id_to_name(transaction.category_id),
                    dbh.account.get_account_name_from_id(transaction.account_id),
                    transaction.note
                ]
            else:
                cur_values = [
                    transaction.date,
                    transaction.amount,
                    transaction.description,
                    cath.category_id_to_name(transaction.category_id),
                    dbh.account.get_account_name_from_id(transaction.account_id),
                    transaction.note
                ]
            values.append(cur_values)
        clip.print_variable_table(headers, values, max_width_column="DESC")


    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # save_statement: saves a categorized statement as a csv
    #   in the case of a Ledger, this is more like an "update" statement
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
                    # print("Added transaction --> " + transaction.printTransaction(False))

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
        self.frame.grid_forget()
        self.frame.destroy()


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







