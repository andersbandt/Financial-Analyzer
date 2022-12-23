from PyPDF2 import PdfFileReader

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction
from gui import gui_helper


class Robinhood(Statement.Statement):
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
            "Robinhood: "
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
            "Extracting raw Robinhood statement at: ",
            self.filepath,
        )

        try:
            with open(self.filepath, "rb") as f:
                reader = PdfFileReader(f)
                contents = reader.getPage(2).extractText().split("\n")
                print(contents)

                # print("Balance Info:")
                # print(contents[22])

                # add starting and ending balance
                balances_string = contents[7]
                print("Balances string:", balances_string)
                whitespace_index = [
                    i for i, c in enumerate(balances_string) if c == " "
                ]

                start_date = contents[4][0:10]
                start_balance = balances_string[
                    whitespace_index[2] + 2 : whitespace_index[3]
                ].replace(",", "")
                print("Start date", start_date)
                print("Start balance", start_balance)

                transactions.append(
                    Transaction.Transaction(
                        start_date,
                        self.account_id,
                        10000000019,
                        start_balance,
                        "BeginningBalance",
                    )
                )  # order: date, account_id, category_id (HARDCODED TO "BALANCE", amount, description

                # add ending balance
                end_date = contents[9]
                end_balance = contents[14][1:].replace(",", "")
                print("End date", end_date)
                print("End balance", end_balance)
                transactions.append(
                    Transaction.Transaction(
                        end_date,
                        self.account_id,
                        10000000019,
                        end_balance,
                        "EndingBalance",
                    )
                )  # order: date, account_id, category_id (HARDCODED TO "BALANCE"), amount, description

                pass

        # handle an invalid file path
        except FileNotFoundError:
            gui_helper.gui_print(
                self.frame, self.prompt, "Uh oh, error in data loading"
            )
            gui_helper.alert_user(
                self.frame, "Missing data!", "You might be missing your marcus.pdf file"
            )
            return False

        # alert user if anything is possibly wrong with the transactions
        error_status = 0
        for transaction in transactions:
            try:
                float(transaction.amount)
            except ValueError as e:
                print("Error: possibly have non float values as amounts:", e)
                error_status = 1

        if error_status:
            gui_helper.alert_user(
                "Error with data scraping",
                "Possibly badly scraped data (amount wrong?)",
                "error",
            )

        # return transactions
        return transactions
