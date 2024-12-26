
# import needed modules
import csv
from loguru import logger

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction


class ChaseCard(Statement.Statement):
    def __init__(self, account_id, year, month, filepath):

        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath)

        # initialize identifying statement info
        self.title = self.title + " - Chase Card"

    # load_statement_data:
    def load_statement_data(self):
        transactions = []
        print("Extracting raw Chase Card statement at: " + self.filepath)

        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")

                # iterate through all the transaction data
                i = 0
                for line in csv_reader:
                    if i > 0:
                        raw_date = line[0]
                        date = (raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5])  # year-month-date
                        transactions.append(Transaction.Transaction(date,
                                                                    self.account_id,
                                                                    None,
                                                                    float(line[5]),
                                                                    line[2],))  # order: date, account_id, category_id, amount, description
                    i += 1
        except FileNotFoundError:
            logger.error("\tMissing data!: You might be missing your Chase Card .csv file")
            return False

        # set and return transactions
        self.transactions = transactions
        return transactions
