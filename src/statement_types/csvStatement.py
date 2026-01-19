"""
@file load_helper.py
@brief tool for helping load in RAW financial data from saved statements on filesystem

"""


# import needed modules
import csv
import os

# import user created modules
import statement_types.Statement as Statement
import statement_types.Transaction as Transaction


# import logger
from loguru import logger

# below are the indexes (column numbers) of the source data from the CSV file
# date
# amount
# description
# category
class csvStatement(Statement.Statement):
    def __init__(self, account_id,
                 year,
                 month,
                 filepath,
                 date_col,
                 amount_col,
                 description_col,
                 category_col,
                 exclude_header=False,
                 inverse_amount=False):
        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath)

        # set the .csv file search column numbering
        self.inverse_amount = inverse_amount
        self.date_col = date_col
        self.amount_col = amount_col
        self.description_col = description_col
        self.category_col = category_col

        self.exclude_header = exclude_header

        # verify .csv extension validity
        file_extension = os.path.splitext(self.filepath)[1]
        if file_extension.lower() != ".csv":
            self.filepath_val = False
        else:
            self.filepath_val = True

        # initialize identifying statement info
        self.title = self.title + " - .csv file"


    def load_statement_data(self):
        # verify statement file integrity
        if self.filepath_val is False:
            logger.debug("Can't load in. Bad filepath for .csv statement: ", self.filepath)
            self.transactions = []
            return

        # loop through .csv file and extract transactions based on supplied parameters
        transactions = []
        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")

                if self.exclude_header:
                    # Skip the header
                    next(csv_reader, None)

                for line in csv_reader:
                    if len(line) == 0:  # NOTE: added check for empty .csv files
                        break

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
                        amount = float(line[self.amount_col])
                    except ValueError as e:
                        logger.debug("ERROR: problem some issue converting numerical values?")
                        print("Can't load in file --> " + self.filepath)
                        raise e
                    if self.inverse_amount:
                        amount = -1*amount

                    try:
                        transactions.append(Transaction.Transaction(date,
                                                                    self.account_id,  # account ID
                                                                    category,  # category
                                                                    amount,  # amount
                                                                    line[self.description_col]  # description
                                                                    ))
                    except Exception as e:
                        print("ERROR: Uh oh, couldn't load transactions based on supplied .csv column params")
                        print(e)
                        print("Can't load in file --> " + self.filepath)
                        raise e # NOTE: never uncomment this line ever. If something is messed up with loading this is the last line

        except FileNotFoundError:
            print("Uh oh, error in data loading")
            print("Missing data! You might be missing your .csv file")
            return False

        # set and return transactions
        self.transactions = transactions
        return transactions
