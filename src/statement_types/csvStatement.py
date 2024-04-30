# import needed modules
import csv
import os

# import user created modules
import statement_types.Statement as Statement
import statement_types.Transaction as Transaction


# below are the indexes (column numbers) of the source data from the CSV file
# date
# amount
# description
# category
class csvStatement(Statement.Statement):
    def __init__(self, account_id, year, month, filepath, date_col, amount_col, description_col, category_col):
        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath)

        # set the .csv file search column numbering
        self.date_col = date_col
        self.amount_col = amount_col
        self.description_col = description_col
        self.category_col = category_col

        # verify .csv extension validity
        file_extension = os.path.splitext(self.filepath)[1]
        if file_extension.lower() != ".csv":
            self.filepath_val = False
        else:
            self.filepath_val = True

        # initialize identifying statement info
        self.title = self.title + " - .csv file"

    def csv_check(self):
        # verify statement file integrity
        if self.filepath_val is not True:
            print("Can't load in. Bad filepath for .csv statement: ", self.filepath)
            return

    def load_statement_data(self):
        # verify statement file integrity
        if self.filepath_val is not True:
            print("Can't load in. Bad filepath for .csv statement: ", self.filepath)
            return

        # loop through .csv file and extract transactions based on supplied parameters
        transactions = []
        print("Extracting .csv statement at: " + self.filepath)
        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")
                for line in csv_reader:
                    raw_date = line[self.date_col]
                    date = (raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5])  # year-month-date

                    if self.category_col > 0:
                        category = line[self.category_col]
                    else:
                        category = None

                    try:
                        transactions.append(Transaction.Transaction(date,
                                                                    self.account_id,  # account ID
                                                                    category,  # category
                                                                    float(line[self.amount_col]),  # amount
                                                                    line[self.description_col]  # description
                                                                    ))
                    except Exception as e:
                        print("Uh oh, couldn't load transactions based on supplied .csv column params")
                        print(e)
                        # raise e

        except FileNotFoundError:
            print("Uh oh, error in data loading")
            print("Missing data! You might be missing your .csv file")
            return False

        # print out some info about transactions
        print("Loaded in " + str(len(transactions)) + " transactions")

        # set and return transactions
        self.transactions = transactions
        return transactions
