"""
Class: Transaction

Transaction represents a single transaction on any statement

"""


class Transaction():
    def __init__(self, date, amount, description, category, source):
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category
        self.source = source

        if self.description is None:
            print("Uh oh, transaction created without description")

    ##############################################################################
    ####      GETTER FUNCTIONS    ################################################
    ##############################################################################

    # getAmount: returns transaction amount
    def getAmount(self):
        return self.amount

    # getCategory: returns transaction category
    def getCategory(self):
        return self.category

    ##############################################################################
    ####      SETTER FUNCTIONS    ################################################
    ##############################################################################

    # setCategory: sets the category
    def setCategory(self, new_category):
        self.category = new_category
        pass

    ##############################################################################
    ####      CATEGORIZATION FUNCTIONS    ########################################
    ##############################################################################

    # categorizeTransactionAutomatic: automatically categorizes a transaction based on the description
    def categorizeTransactionAutomatic(self, categories):
        if self.description == "" or self.description == None:
            print("Uh oh, description doesn't exist for this transaction")

        if self.category is None:
            for category in categories:  # iterate through all provided Category objects in array
                if category.keyword is None:
                    print("Weird, a category has no keywords associated with it... that shouldn't happen")
                if any(keyword in self.description for keyword in category.keyword):
                    self.category = category.name
                    return
        else:
            print("Uh oh, transaction already has category assigned")
            return

        self.category = "NA"  # if no appropriate category was found

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
        if self.category != None:
            stringToPrint = stringToPrint + " || CATEGORY: " + ''.join(self.category)

        return stringToPrint

    # getSaveString: gets an array of what to save to CSV file for the transaction
    def getSaveStringArray(self):
        saveStringArray = [''.join(self.date), ''.join(str(self.amount)), ''.join(self.description)]

        if self.category != None:
            saveStringArray.append(''.join(self.category))

        return saveStringArray

    # getStringDict: returns a string of transaction content contained in a dictionary
    def getStringDict(self):
        string_dict = {
            "date": self.date,
            "amount": str(self.amount),
            "description": str(self.description),
            "category": self.category,
            "source": self.source
        }

        return string_dict
