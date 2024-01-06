"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

# import user defined modules
import db.helpers as dbh
import statement_types.Ledger as Ledger
import cli.cli_helper as clih
import tools.load_helper as loadh


class Statement(Ledger.Ledger):
    def __init__(self, account_id, year, month, filepath, transactions=None):
        # set Statement title based on account_id and date info
        self.title = f"{year}-{month} for {account_id}"

        # call parent class __init__ method
        # super(Ledger.Ledger, self).__init__(master, title, row_num, column_num, *args, **kwargs)
        super().__init__(self.title, transactions=transactions)

        # initialize identifying statement info
        self.account_id = account_id
        self.year = year
        self.month = month
        self.filepath = filepath

    ##############################################################################
    ####      DATA LOADING FUNCTIONS    ##########################################
    ##############################################################################

    # create_statement_data: combines and automatically categorizes transactions across all raw account statement data
    def create_statement_data(self):
        print("Creating statement data for", self.title)
        self.transactions.extend(self.load_statement_data())

        # check for if transactions actually got loaded in
        if len(self.transactions) == 0:
            print("Uh oh, something went wrong retrieving transactions. Likely the transaction data is corrupt and resulted in 0 transactions. Exiting statement data creation.")
            return False

        print("Loaded in raw transaction data, running categorizeStatementAutomatic() now!")

        self.categorizeStatementAutomatic()  # run categorizeStatementAutomatic on the transactions
        print("Statement should be loaded and displayed")

    # load_statement_data: this function should be defined per account's Statement class
    # DO NOT DELETE
    def load_statement_data(self):
        pass


    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # save_statement: saves a categorized statement as a csv
    def save_statement(self):
        print("Attempting to save statement...")

        # check statement "save status" and ask user for save verification
        if self.check_statement_status(self.transactions):
            response = clih.promptYesNo("It looks like a saved statement for " + self.title + " already exists, are you sure you want to overwrite by saving this one?")
            if response is False:
                print("Ok, aborting save statement")
                return False

        # DATA INTEGRITY / ERROR CHECKING ON TRANSACTION
        error_flag = 0
        for transaction in self.transactions:
            # TODO: add some confirmation if user actually wants to add transaction for duplicates
            loaded = loadh.check_transaction_load_status(transaction)
            if loaded:
                transaction.note = "duplicate ?"
                print("Uh oh, is this transaction already in the ledger??? --> " + transaction.printTransaction(
                    False))  # the 'False' flag controls the actual function doing the printing
                error_flag = 1

        # USER CONFIRMATION
        if error_flag == 1:
            res = clih.promptYesNo("It looks like some duplicates or something were detected... are you sure you want to add this statement?")
            if not res:
                print("Ok, aborting save statement!")
                return False

        # INSERT TRANSACTION
        # error_flag = 0
        # for transaction in self.transactions:
        #     success = dbh.ledger.insert_transaction(transaction)
        #     if success == 0:
        #         error_flag = 1

        # FINAL ERROR HANDLING
        if error_flag == 1:
            clih.alert_user(
                "Error in ledger adding!",
                "At least 1 thing went wrong adding to ledger",
            )
            return False
        else:
            print("Saved statement")
        return True

