"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

# import user defined modules
import db.helpers as dbh
import statement_types.Ledger as Ledger
import cli.cli_helper as clih
import categories.categories_helper as cath


class Statement(Ledger.Ledger):
    def __init__(self, account_id, year, month, filepath, transactions=None):
        # set Statement title based on account_id and date info
        self.title = str(year) + "-" + str(month) + " :" + str(account_id)

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
        if self.check_statement_status(self.load_statement_data()):
                print("Uh oh, looks like data already exists for this particular statement")
                res = clih.promptYesNo("Data might already be loaded in for this statement... do you want to continue?")
                if res is False:
                    print("Ok, not loading in statement")
                    return

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

    # TODO: failing when I try to load in Marcus statement data... however it is loading in erroneously
    # check_statement_status: returns True if data already exists for this statement, False otherwise
    def check_statement_status(self, current_transactions):
        # handle leading 0 for months less than 10 (before October)
        if self.month >= 10:
            month_start = str(self.year) + "-" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + str(self.month) + "-" + "31"
        else:
            month_start = str(self.year) + "-" + "0" + str(self.month) + "-" + "01"
            month_end = str(self.year) + "-" + "0" + str(self.month) + "-" + "31"

        loaded_transactions = dbh.ledger.get_account_transactions_between_date(
            self.account_id, month_start, month_end
        )

        # compare to loaded length of transactions
        if len(loaded_transactions) == len(current_transactions):
            if (
                len(loaded_transactions) != 0
            ):  # prevents alerting when data might not be loading in correctly
                print("Uh oh, has this data been loaded in already?")
                # sanity check a couple transactions??
                return True
        else:
            return False

    ##############################################################################
    ####      DATA SAVING FUNCTIONS    ###########################################
    ##############################################################################

    # TODO: make green/red checkmarks update upon completion of this (for Statement only)
    #   also - make Category dropdowns on transactions lines change into written text that can be double clicked
    # save_statement: saves a categorized statement as a csv
    def save_statement(self):
        print("Attempting to save statement...")

        # check statement "save status" and ask user for save verificaiton
        if self.check_statement_status(self.transactions):
            response = clih.promptYesNo("It looks like a saved statement for " + self.title + " already exists, are you sure you want to overwrite by saving this one?")
            if response is False:
                print("Ok, not saving statement")
                return False

        # iterate through transactions and  insert into database
        error_status = 0
        for transaction in self.transactions:
            success = dbh.ledger.insert_transaction(transaction)
            if success == 0:
                error_status = 1

        # error handling
        if error_status == 1:
            clih.alert_user(
                "Error in ledger adding!",
                "At least 1 thing went wrong adding to ledger",
            )
            return False
        else:
            print("Saved statement")
        return True
