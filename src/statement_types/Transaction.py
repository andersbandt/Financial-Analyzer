"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

# import needed modules
from dateutil.parser import parse

# import user created modules
import db.helpers as dbh

class Transaction:
    def __init__(self, date, account_id, category_id, amount, description, note=None, sql_key=None):
        self.account_id = account_id
        self.category_id = category_id
        self.date = date
        self.amount = amount
        self.note = note
        self.description = description

        # try:
        #     if self.amount[0] == "$":
        #         self.amount = self.amount[1 : len(self.amount)]
        # except TypeError as e:
        #     pass

        try:
            self.amount = float(self.amount)
        except ValueError as e:
            print("ERROR: couldn't create transaction: ", description)
            print("Something went wrong creation transaction: ", e)
            return

        # create SQL key (optional parameter)
        if sql_key is not None:
            self.sql_key = sql_key
        else:
            self.sql_key = None

        # __init__ error handling
        if self.description is None:
            print("Uh oh, transaction created without description")

        self.check_date()
        self.check_amount()

    # check_date: checks if a Transaction date variable is valid
    def check_date(self):
        if self.date:
            try:
                parse(self.date)
                return True
            except:
                print("ERROR (TRANSACTION): date might be wrong")
                return False
        return False

    # check_amount: checks if a Transaction amount variable is valid
    def check_amount(self):
        if type(self.amount) is float:
            return True

        if type(self.amount) is str:
            result = self.amount.find(",")

            if result != -1:
                print(
                    "ERROR (TRANSACTION): transaction might be loaded in with a comma (big no no)"
                )
                return False
            else:
                return True

        return True

    ##############################################################################
    ####      GETTER FUNCTIONS    ################################################
    ##############################################################################

    # getAmount: returns transaction amount
    def getAmount(self):
        return self.amount

    # get_category_string: returns transaction's category as a string
    def get_category_string(self):
        pass
        # return category_helper.category_id_to_name(self.category_id)

    def get_cat_status(self):
        if self.category_id == 0:
            return False
        else:
            return True

    ##############################################################################
    ####      SETTER FUNCTIONS    ################################################
    ##############################################################################

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
                # if category.keyword is None:
                #   print("Weird, a category has no keywords associated with it... that shouldn't happen")
                try:
                    if any(keyword in self.description.upper() for keyword in category.keyword):
                        self.category_id = category.id
                except Exception as e:
                    print("ERROR: couldn't automatically categorize transaction:", e)

        # if there is already a category ID
        else:
            print("Uh oh, transaction already has category assigned.")
            return

        # if no category got assigned set as NA category (0)
        if self.category_id is None:
            self.category_id = 0

    # categorizeTransactionManual: manually categorizes a transaction using input description
    # def categorizeTransactionManual(self, description):
    #     self.description = description

    ##############################################################################
    ####      PRINTING FUNCTIONS           #######################################
    ##############################################################################

    # getSpaces: gets the number of spaces needed for pretty printing in straight columns
    def getSpaces(self, length, trim):
        spaces = ""
        for i in range(trim - length):
            spaces += " "
        return spaces

    # printTransaction: pretty prints a single transaction
    def printTransaction(self, print_mode=True, include_sql_key=False):
        if include_sql_key:
            stringToPrint = "KEY: " + "".join(str(self.sql_key)) + "    "
        else:
            stringToPrint = ""

        # add remaining columns
        stringToPrint += (
            "DATE: "
            + "".join(self.date)
            + " || AMOUNT: "
            + "".join(str(self.amount))
            + self.getSpaces(len(str(self.amount)), 8)
            + " || DESC: "
            + "".join(self.description[0:80])
            + self.getSpaces(len(self.description), 80)
        )
        if self.category_id is not None:
            category_name = dbh.category.get_category_name_from_id(self.category_id)
            stringToPrint = stringToPrint + " || CATEGORY: " + str(category_name) + self.getSpaces(len(str(category_name)), 15)

        stringToPrint = stringToPrint + " || ACCOUNT: " + "".join(
            dbh.account.get_account_name_from_id(self.account_id)) + self.getSpaces(len(str(self.account_id)), 18)

        if self.note is not None:
            stringToPrint = stringToPrint + " || NOTE: " + self.note

        if print_mode:
            print(stringToPrint)
        return stringToPrint


    # getSaveString: gets an array of what to save to CSV file for the transaction
    # NOTE: where is this function used? What is it actually doing?
    #   check where I call
    def getSaveStringArray(self):
        saveStringArray = [
            "".join(self.date),
            "".join(str(self.amount)),
            "".join(self.description),
        ]

        if self.category_id != None:
            saveStringArray.append("".join(self.category_id))

        return saveStringArray

    # getStringDict: returns a string of transaction content contained in a dictionary
    def getStringDict(self):
        string_dict = {
            "sql_key": self.sql_key,
            "date": self.date,
            "amount": str(self.amount),
            "description": str(self.description),
            "category": self.category_id,
            "source": self.account_id,
        }

        return string_dict
