"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

# import needed modules
from dateutil.parser import parse

# import user created modules
import db.helpers as dbh
from categories import categories_helper as cath


class Transaction:
    def __init__(self, date, account_id, category_id, value, description, note=None, sql_key=None,
                 plaid_transaction_id=None, plaid_account_id=None,
                 transaction_source='MANUAL', plaid_synced_at=None):
        self.account_id = account_id
        self.category_id = category_id
        self.date = date
        self.value = value
        self.note = note
        self.description = description

        # Plaid-specific fields (optional, for backward compatibility)
        self.plaid_transaction_id = plaid_transaction_id
        self.plaid_account_id = plaid_account_id
        self.transaction_source = transaction_source  # 'PLAID', 'CSV', or 'MANUAL'
        self.plaid_synced_at = plaid_synced_at

        try:
            self.value = float(self.value)
        except ValueError as e:
            print("ERROR: couldn't create transaction: ", description)
            print("Something went wrong creation transaction: ", e)
            return

        # create SQL key (optional parameter)
        if sql_key is not None:
            self.sql_key = int(sql_key)

        # __init__ error handling
        if self.description is None:
            print("Uh oh, transaction created without description")
            self.description = ''

        self.check_date()
        self.check_amount()

    # check_date: checks if a Transaction date variable is valid
    def check_date(self):
        if self.date:
            parse(self.date)
            return True
        return False

    # check_amount: checks if a Transaction amount variable is valid
    def check_amount(self):
        if type(self.value) is float:
            return True

        if type(self.value) is str:
            result = self.value.find(",")

            if result != -1:
                print(
                    "ERROR (TRANSACTION): transaction might be loaded in with a comma (big no no)"
                )
                return False
            else:
                return True

        return True

    ##############################################################################
    ####      SETTER and GETTER FUNCTIONS    #####################################
    ##############################################################################

    # getAmount: returns transaction.value
    def getAmount(self):
        return self.value

    # get_category_string: returns transaction's category as a string
    def get_category_string(self):
        pass
        # return category_helper.category_id_to_name(self.category_id)

    def get_cat_status(self):
        if self.category_id == 0:
            return False
        else:
            return True

    # setCategory: sets the category
    def setCategory(self, c_id):
        self.category_id = c_id
        pass

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeTransactionAutomatic: automatically categorizes a transaction based on the description
    def categorizeTransactionAutomatic(self, categories):
        # if the description is missing or blank
        if self.description == "" or self.description is None:
            print(
                "Uh oh, description doesn't exist for this transaction. Unable to automatically categorize."
            )

        # if the category ID is blank (able to assign a new one)
        if self.category_id is None or self.category_id == 0:
            for (category) in categories:  # iterate through all provided Category objects in array
                try:
                    for keyword in category.keyword:
                        if keyword in self.description.upper():
                            # ASSIGN CATEGORY, EDIT/CREATE NOTE, and EXIT
                            self.category_id = category.id
                            if self.note is not None:
                                self.note = self.note + ";keyword=" + keyword
                            else:
                                self.note = f"keyword={keyword}"
                            return True
                except Exception as e:
                    print("ERROR: couldn't automatically categorize transaction:", e)

        # if there is already a category ID
        else:
            print("Uh oh, transaction already has category assigned.")
            return False

        # if no category got assigned set as NA category (0)
        if self.category_id is None:
            self.category_id = 0

    ##############################################################################
    ####      PRINTING FUNCTIONS           #######################################
    ##############################################################################

    # getSpaces: gets the number of spaces needed for pretty printing in straight columns
    def getSpaces(self, length, trim):
        spaces = ""
        for i in range(trim - length):
            spaces += " "
        return spaces

    # print_trans: pretty prints a single transaction
    def print_trans(self, print_mode=True, include_sql_key=False, trim=80):
        if include_sql_key:
            prnt_str = "KEY: " + "".join(str(self.sql_key)) + "    "
        else:
            prnt_str = ""

        # truncate description to trim length
        truncated_desc = self.description[0:trim] if len(self.description) > trim else self.description

        # add remaining columns
        prnt_str += (
                "DATE: "
                + "".join(self.date)
                + " || AMOUNT: "
                + "".join(str(self.value))
                + self.getSpaces(len(str(self.value)), 8)
                + " || DESC: "
                + "".join(truncated_desc)
                + self.getSpaces(len(truncated_desc), trim)
        )

        if self.category_id is not None:
            category_name = dbh.category.get_category_name_from_id(self.category_id)
            prnt_str = prnt_str + " || CATEGORY: " + str(category_name) + self.getSpaces(
                len(str(category_name)), 15)

        prnt_str = prnt_str + " || ACCOUNT: " + "".join(
            dbh.account.get_account_name_from_id(self.account_id)) + self.getSpaces(len(str(self.account_id)), 18)

        if self.note is not None:
            prnt_str = prnt_str + " || NOTE: " + self.note

        if print_mode:
            print(prnt_str)
        return prnt_str

    # getStringDict: returns a string of transaction content contained in a dictionary
    def getStringDict(self):
        string_dict = {
            "sql_key": self.sql_key,
            "date": self.date,
            "amount": str(self.value),
            "description": str(self.description),
            "category": self.category_id,
            "source": self.account_id,
        }

        return string_dict





