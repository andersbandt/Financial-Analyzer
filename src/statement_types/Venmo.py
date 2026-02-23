
# import needed modules
import csv
import os

# import my created modules
import statement_types.csvStatement as csvStatement
import statement_types.Transaction as Transaction


# TODO: need to figure out how to tack on person of interest
#   the "FROM" column is always the person who initiated the request, not just where the money is going
# @brief class description for Venmo statement
# @desc This class parses ONLY statements that have a funding source of a Venmo balance
#     or transactions that are deposits into Venmo
class Venmo(csvStatement.csvStatement):
    def __init__(self, account_id, year, month, filepath, date_col, amount_col, description_col, category_col, exclude_header=False, inverse_amount=False):
        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath, date_col, amount_col, description_col, category_col, exclude_header=exclude_header, inverse_amount=inverse_amount)

        # verify .csv extension validity
        file_extension = os.path.splitext(self.filepath)[1]
        if file_extension.lower() != ".csv":
            self.filepath_val = False
        else:
            self.filepath_val = True

        # initialize identifying statement info
        self.title = self.title + " - Venmo"

    def load_statement_data(self):
        # verify statement file integrity
        if self.filepath_val is not True:
            print("Can't load in. Bad filepath for .csv statement: ", self.filepath)
            return

        transactions = []
        try:
            with open(self.filepath, encoding='utf-8') as f:
                csv_reader = csv.reader(f, delimiter=",")
                for line in csv_reader:
                    # if the ID column is populated (to avoid blank lines from being categories
                    if line[1] != "" and line[1] != 'ID':
                        date = line[2][0:10]

                        # get raw amount (NO SIGN INFORMATION)

                        # Replace the comma with an empty string and then convert to float\
                        input_float_string = line[8][3:]
                        amount = float(input_float_string.replace(',', ''))
                        if line[8][0] == '-':
                            amount = -1 * amount

                        description = (
                                line[6] + "<->" + line[7] + " : " + line[5]
                        )  # person receiving it + description

                        transactions.append(
                            Transaction.Transaction(
                                date, self.account_id, None, amount, description, note=line[3]
                            )
                        )  # order: date, account_id, category_id, amount, description

        except FileNotFoundError:
            print("You might be missing your Venmo .csv file")
            return False

        # set and return transactions
        self.transactions = transactions
        return transactions
