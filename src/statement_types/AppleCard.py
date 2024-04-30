

# import needed modules
import csv

import statement_types.Statement as Statement
import statement_types.csvStatement as csvStatement
import statement_types.Transaction as Transaction


class AppleCard(csvStatement.csvStatement):
    def __init__(self, account_id, year, month, filepath, date_col, amount_col, description_col, category_col):

        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath, date_col, amount_col, description_col, category_col)

        # initialize identifying statement info
        self.title = ("AppleCard: " + str(self.account_id) + ":" + str(self.year) + "-" + str(self.month))


    # load_statement_data:
    def load_statement_data(self):
        if self.filepath_val is not True:
            print("Can't load in. Bad filepath for .csv statement: ", self.filepath)
            return

        transactions = []
        print("Extracting raw Apple Card statement at: " + self.filepath)

        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")

                # iterate through all the transaction data
                i = 0
                for line in csv_reader:
                    if i > 0:
                        raw_date = line[1]
                        date = (
                            raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5]
                        )  # year-month-date
                        transactions.append(
                            Transaction.Transaction(
                                date,
                                self.account_id,
                                None,
                                -1 * float(line[6]),
                                line[2],
                            )
                        )  # order: date, account_id, category_id, amount, description
                    i += 1
        except FileNotFoundError:
            return False

        # set and return transactions
        self.transactions = transactions
        return transactions
