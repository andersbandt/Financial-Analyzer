import csv

from Statement_Classes import Statement
from Statement_Classes import Transaction

from Finance_GUI import gui_helper

# TODO: data not loading in
# TODO: data may seem to be loading in as strings instead of floats. Dollar sign may also be in amounts
# @brief class description for Venmo statement
# @desc This class parses ONLY statements that have a funding source of a Venmo balance
#     or transactions that are deposits into Venmo
class Venmo(Statement.Statement):

    def load_statement_data(self):
        transactions = []
        gui_helper.gui_print(self.frame, self.prompt, "Extracting raw Venmo statement at: ", self.filepath)
        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=',')
                for line in csv_reader:
                    #print(line)
                    # examine withdrawals (funding source for the transaction is equal to "Venmo balance")
                    if line[11] == "Venmo balance":
                        date = line[2][0:10]
                        amount = line[8][0] + line[8][3:]  # first grab the sign (always negative?) and then add the value without a dollar sign
                        description = line[7] + "-" + line[5]  # person receiving it + description
                        transactions.append(Transaction.Transaction(date, self.account_id, None, amount, description))  # order: date, account_id, category_id, amount, description

                    # examine deposits (destination source for the transaction is equal to "Venmo balance")
                    if line[12] == "Venmo balance":
                        date = line[2][0:10]
                        amount = line[8][2:]  # grab everything but the dollar sign
                        description = line[6] + "-" + line[5]  # person that sent + description
                        transactions.append(Transaction.Transaction(date, self.account_id, None, amount, description))  # order: date, account_id, category_id, amount, description
        except FileNotFoundError:
            gui_helper.gui_print(self.frame, self.prompt, "Uh oh, error in data loading")
            gui_helper.alert_user(self.frame, "Missing data!", "You might be missing your Wells Fargo Credit .csv file")
            return False

        return transactions
