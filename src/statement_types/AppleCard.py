# import needed moodules
import csv

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction
from gui import gui_helper


class AppleCard(Statement.Statement):
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
            "AppleCard: "
            + str(self.account_id)
            + ":"
            + str(self.year)
            + "-"
            + str(self.month)
        )

    # load_statement_data:
    def load_statement_data(self):
        transactions = []
        gui_helper.gui_print(
            self.frame,
            self.prompt,
            "Extracting raw Apple Card statement at: ",
            self.filepath,
        )

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
            gui_helper.gui_print(
                self.frame, self.prompt, "Uh oh, error in data loading"
            )
            gui_helper.alert_user(
                self.frame,
                "Missing data!",
                "You might be missing your Apple Card .csv file",
            )
            return False

        # return transactions
        return transactions
