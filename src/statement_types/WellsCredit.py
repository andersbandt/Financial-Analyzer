import csv

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction


class WellsCredit(Statement.Statement):
    def __init__(
        self,
        master,
        account_id,
        year,
        month,
        file,
        row_num,
        column_num,
        *args,
        **kwargs
    ):
        # call parent class __init__ method
        # super(Statement.Statement, self).__init__(master, account_id, year, month, file, row_num, column_num, *args, **kwargs)
        super().__init__(
            master, account_id, year, month, file, row_num, column_num, *args, **kwargs
        )

        # initialize identifying statement info
        self.title = (
            "Wells Credit: "
            + str(self.account_id)
            + ":"
            + str(self.year)
            + "-"
            + str(self.month)
        )

    # loadWellsFargoCredit: loads data from file 'Checking1.csv' from Wells Fargo account
    # below are the indexes (column numbers) of the source data from the CSV file
    # 0: date
    # 1: amount
    # 4: description
    def load_statement_data(self):
        transactions = []
        gui_helper.gui_print(
            self.frame,
            self.prompt,
            "Extracting raw Wells Credit statement at: ",
            self.filepath,
        )
        try:
            with open(self.filepath) as f:
                csv_reader = csv.reader(f, delimiter=",")
                for line in csv_reader:
                    raw_date = line[0]
                    date = raw_date[6:10] + "-" + raw_date[0:2] + "-" + raw_date[3:5]
                    transactions.append(
                        Transaction.Transaction(
                            date, self.account_id, None, float(line[1]), line[4]
                        )
                    )  # order: date, account_id, category_id, amount, description
        except FileNotFoundError:
            gui_helper.gui_print(
                self.frame, self.prompt, "Uh oh, error in data loading"
            )
            gui_helper.alert_user(
                self.frame,
                "Missing data!",
                "You might be missing your Wells Fargo Credit .csv file",
            )
            return False

        return transactions
