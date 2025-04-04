"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

# import needed modules
from dateutil.parser import parse

# import user created modules
import db.helpers as dbh
from analysis import investment_helper as invh
from categories import categories_helper as cath


class Transaction:
    def __init__(self, date, account_id, category_id, amount, description, note=None, sql_key=None):
        self.account_id = account_id
        self.category_id = category_id
        self.date = date
        self.amount = amount
        self.note = note
        self.description = description

        try:
            self.amount = float(self.amount)
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
    ####      SETTER and GETTER FUNCTIONS    #####################################
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
    # TODO: make this `trim` variable better (apply to generic columns)
    def print_trans(self, print_mode=True, include_sql_key=False, trim=80):
        # TODO: eliminate this check for description type
        if self.description is None:
            self.description = ''

        if include_sql_key:
            prnt_str = "KEY: " + "".join(str(self.sql_key)) + "    "
        else:
            prnt_str = ""

        # add remaining columns
        prnt_str += (
                "DATE: "
                + "".join(self.date)
                + " || AMOUNT: "
                + "".join(str(self.amount))
                + self.getSpaces(len(str(self.amount)), 8)
                + " || DESC: "
                + "".join(self.description[0:80])
                + self.getSpaces(len(self.description), trim)
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
            "amount": str(self.amount),
            "description": str(self.description),
            "category": self.category_id,
            "source": self.account_id,
        }

        return string_dict


class InvestmentTransaction(Transaction):
    def __init__(self, date, account_id, category_id, ticker, shares, trans_type, value, description, note=None,
                 sql_key=None):
        super().__init__(date, account_id, category_id, value, description, note, sql_key)

        self.ticker = ticker
        self.shares = shares
        self.trans_type = trans_type
        self.value = value
        self.strike_price = self.value/self.shares
        self.price = 0
        self.gain = 0

        self.update_price()

    def update_price(self):
        self.price = invh.get_ticker_price(self.ticker)

    def get_price(self):
        return round(self.price, 2)

    def get_gain(self):
        try:
            self.gain = self.price/self.strike_price
            self.gain = (self.gain - 1)*100  # express gain in percent
        except ZeroDivisionError:
            self.gain = 0

        return round(self.gain, 3)

# TODO: somehow capture in Obsidian or something that this thing exists and like class structure and shit
    def print_trans(self, print_mode=True, include_sql_key=False):
        # add some InvestmentTransaction specific information
        prnt_str = " || TICKER: " + "".join(
            self.ticker + self.getSpaces(len(str(self.account_id)), 14))

        prnt_str = prnt_str + " || PRICE: " + "".join(
            "$ " + str(self.get_price()) + self.getSpaces(len(str(self.account_id)), 14))

        prnt_str = prnt_str + " || GAIN: " + "".join(
            str(self.get_gain()) + "%" + self.getSpaces(len(str(self.account_id)), 13))

        # add main Transaction stuff
        tmp_note = self.note
        self.note = None
        prnt_str = prnt_str + super().print_trans(print_mode=False, include_sql_key=include_sql_key, trim=35)
        self.note = tmp_note  # so hack lmao

        if print_mode:
            print(prnt_str)
        return prnt_str


