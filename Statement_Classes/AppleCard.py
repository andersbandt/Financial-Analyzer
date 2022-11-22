
# import needed moodules
from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper

import csv


class AppleCard(Statement.Statement):
    # load_statement_data:
    def load_statement_data(self):
        transactions = []
        gui_helper.gui_print(self.frame, self.prompt, "Extracting raw Apple Card statement at: ", self.filepath)

        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=',')


                # iterate through all the transaction data
                i = 0
                for line in csv_reader:
                    if i > 0:
                        raw_date = line[1]
                        date = raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5]  # year-month-date
                        transactions.append(Transaction.Transaction(date, self.account_id, None, float(line[6]), line[2]))  # order: date, account_id, category_id, amount, description
                    i += 1
        except FileNotFoundError:
            gui_helper.gui_print(self.frame, self.prompt, "Uh oh, error in data loading")
            gui_helper.alert_user(self.frame, "Missing data!", "You might be missing your Apple Card .csv file")
            return False

        # return transactions
        return transactions
