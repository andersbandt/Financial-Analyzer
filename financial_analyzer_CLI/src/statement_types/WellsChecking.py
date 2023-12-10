
# import needed modules
import csv

# import user created modules
import statement_types.Statement as Statement
import statement_types.Transaction as Transaction


class WellsChecking(Statement.Statement):
    def __init__(self, account_id, year, month, filepath):
        # call parent class __init__ method
        super().__init__(account_id, year, month, filepath)

        # initialize identifying statement info
        self.title = ("Wells Checking: " + str(self.account_id) + ":" + str(self.year) + "-" + str(self.month))

    # loadWellsFargoCredit: loads data from file 'Checking1.csv' from Wells Fargo account
    # below are the indexes (column numbers) of the source data from the CSV file
    # 0: date
    # 1: amount
    # 4: description
    def load_statement_data(self):
        transactions = []
        print("Extracting raw Wells Checking statement at: " + self.filepath)
        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")
                for line in csv_reader:
                    raw_date = line[0]
                    date = (raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5])  # year-month-date
                    transactions.append(Transaction.Transaction(date, self.account_id, None, float(line[1]), line[4]))  # order: date, account_id, category_id, amount, description
        except FileNotFoundError:
            print("Uh oh, error in data loading")
            print("Missing data! You might be missing your Wells Fargo Credit .csv file")
            return False

        # print out some info about transactions
        print("Loaded in " + str(len(transactions)) + " transactions")

        # set and return transactions
        self.transactions = transactions
        return transactions
