

# import needed modules
import csv
import os

# import user created modules
import statement_types.csvStatement as csvStatement
import statement_types.Transaction as Transaction


# below are the indexes (column numbers) of the source data from the CSV file
# date
# amount
# description
# category
class CitiMastercard(csvStatement.csvStatement):
    def __init__(self, account_id,
                 year,
                 month,
                 filepath,
                 date_col,
                 debit_col,
                 credit_col,
                 description_col,
                 category_col,
                 exclude_header=False):
        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath, date_col, debit_col, description_col, category_col, exclude_header=exclude_header)

        # set the .csv file search column numbering
        self.amount_col = None
        self.debit_col = debit_col
        self.credit_col = credit_col


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

                if self.exclude_header:
                    # Skip the header
                    next(csv_reader, None)

                for line in csv_reader:
                    # DATE
                    raw_date = line[self.date_col]
                    date = (raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5])  # year-month-date

                    # CATEGORY
                    if self.category_col > 0:
                        category = line[self.category_col]
                    else:
                        category = None

                    # AMOUNT
                    try:
                        amount = -1 * float(line[self.debit_col])
                    except ValueError:
                        amount = -1 * float(line[self.credit_col])

                    try:
                        transactions.append(Transaction.Transaction(date,
                                                                    self.account_id,  # account ID
                                                                    category,  # category
                                                                    amount,  # amount
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
