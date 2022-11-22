"""
Class: Transaction

Transaction represents a single transaction on any statement

"""

from dateutil.parser import parse

class Transaction:
    def __init__(self, date, account_id, category_id, amount, description, *args):
        self.date = date
        self.account_id = account_id
        self.category_id = category_id
        self.amount = amount
        self.description = description

        try:
            if self.amount[0] == '$':
                self.amount = self.amount[1:len(self.amount)]
        except TypeError as e:
            pass

        try:
            self.amount = float(self.amount)
        except ValueError as e:
            print("ERROR: couldn't create transaction: ", description)
            print("Something went wrong creation transaction: ", e)
            return

        # create SQL key (optional parameter)
        try:
            self.sql_key = args[0]
        except IndexError as e:
            self.sql_key = None
            pass

        # __init__ error handling
        if self.description is None:
            print("Uh oh, transaction created without description")

        self.check_date()
        self.check_amount()

    #check_date: checks if a Transaction date variable is valid
    def check_date(self):
        if self.date:
            try:
                parse(self.date)
                return True
            except:
                print("ERROR (TRANSACTION): date might be wrong")
                return False
        return False

    #check_amount: checks if a Transaction amount variable is valid
    def check_amount(self):
        if type(self.amount) is float:
            return True

        if type(self.amount) is str:
            result = self.amount.find(',')

            if result != -1:
                print("ERROR (TRANSACTION): transaction might be loaded in with a comma (big no no)")
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
        #return category_helper.category_id_to_name(self.category_id)

    ##############################################################################
    ####      SETTER FUNCTIONS    ################################################
    ##############################################################################

    # setCategory: sets the category
    def setCategory(self, new_category):
        self.category_id = new_category
        pass

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeTransactionAutomatic: automatically categorizes a transaction based on the description
    def categorizeTransactionAutomatic(self, categories):
        # if the description is missing or blank
        if self.description == "" or self.description is None:
            print("Uh oh, description doesn't exist for this transaction. Unable to automatically categorize.")

        # if the category ID is blank (able to assign a new one)
        if self.category_id is None or self.category_id == 0:
            for category in categories:  # iterate through all provided Category objects in array
                #if category.keyword is None:
                #   print("Weird, a category has no keywords associated with it... that shouldn't happen")
                if any(keyword in self.description for keyword in category.keyword):
                    self.category_id = category.category_id

        # if there is already a category ID
        else:
            print("Uh oh, transaction already has category assigned.")
            return

        # if no category got assigned
        if self.category_id is None: self.category_id = 0


    # categorizeTransactionManual: manually categorizes a transaction using input description
    def categorizeTransactionManual(self, description):
        self.description = description

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
    def printTransaction(self):
        stringToPrint = ("DATE: " + ''.join(self.date) + \
                         " || AMOUNT: " + ''.join(str(self.amount)) + self.getSpaces(len(str(self.amount)), 8) + \
                         " || DESC: " + ''.join(self.description[0:40]) + self.getSpaces(len(self.description), 40))
        if self.category_id is not None:
            stringToPrint = stringToPrint + " || CATEGORY: " + str(self.category_id)

        print(stringToPrint)

        return stringToPrint

    # getSaveString: gets an array of what to save to CSV file for the transaction
    def getSaveStringArray(self):
        saveStringArray = [''.join(self.date), ''.join(str(self.amount)), ''.join(self.description)]

        if self.category_id != None:
            saveStringArray.append(''.join(self.category_id))

        return saveStringArray

    # getStringDict: returns a string of transaction content contained in a dictionary
    def getStringDict(self):
        string_dict = {
            "date": self.date,
            "amount": str(self.amount),
            "description": str(self.description),
            "category": self.category_id,
            "source": self.account_id
        }

        return string_dict
