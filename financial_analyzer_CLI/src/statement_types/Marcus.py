import csv

from PyPDF2 import PdfFileReader

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction
from tools import date_helper


class Marcus(Statement.Statement):
    def load_statement_data(self):
        transactions = []
        gui_helper.gui_print(
            self.frame,
            self.prompt,
            "Extracting raw Marcus statement at: ",
            self.filepath,
        )

        try:
            with open(self.filepath, "rb") as f:
                reader = PdfFileReader(f)
                contents = reader.getPage(0).extractText().split("\n")
                print(contents)

                # print("Balance Info:")
                # print(contents[22])

                # add starting balance
                starting_balance_string = contents[29]
                # print("Starting balance")
                # print(starting_balance_string)
                whitespace_index = [
                    i for i, c in enumerate(starting_balance_string) if c == " "
                ]

                start_date = starting_balance_string[0 : whitespace_index[0]]
                start_balance = starting_balance_string[whitespace_index[1] + 2 :]
                print("Start date", start_date)
                print("Start balance", start_balance)
                transactions.append(
                    Transaction.Transaction(
                        start_date,
                        self.account_id,
                        10000000014,
                        start_balance,
                        "BeginningBalance",
                    )
                )  # order: date, account_id, category_id (HARDCODED TO "BALANCE", amount, description

                # add ending balance
                ending_balance_string = contents[31]
                # print("Starting balance")
                # print(starting_balance_string)
                whitespace_index = [
                    i for i, c in enumerate(ending_balance_string) if c == " "
                ]

                end_date = ending_balance_string[0 : whitespace_index[0]]
                end_balance = ending_balance_string[whitespace_index[1] + 2 :]
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

                # get interest info
                interest_string = contents[24]
                # print("Interest String:", interest_string)

                whitespace_index = interest_string.index(" ")
                interest_amount = interest_string[
                    whitespace_index + 2 :
                ]  # plus 2 to move past the first whitespace and the dollar sign
                interest_date = end_date

                print("Interest date:", interest_date)
                print("Interest amount:", interest_amount)
                transactions.append(
                    Transaction.Transaction(
                        interest_date,
                        self.account_id,
                        10000000024,
                        interest_amount,
                        "InterestPaidthisPeriod",
                    )
                )  # order: date, account_id, category_id (HARDCODED TO "INTEREST"), amount, description

                # add deposit info
                deposit_string = contents[23]
                print("Deposit String:", deposit_string)

                whitespace_index = deposit_string.index(" ")
                deposit_amount = deposit_string[
                    whitespace_index + 2 :
                ]  # plus 2 to move past the first whitespace and the dollar sign
                deposit_date = end_date

                print("Deposit date:", deposit_date)
                print("Deposit amount:", deposit_amount)
                transactions.append(
                    Transaction.Transaction(
                        deposit_date,
                        self.account_id,
                        None,
                        deposit_amount,
                        "DepositsandOtherCredits",
                    )
                )  # order: date, account_id, category_id, amount, description

                # add withdrawals info
                withdrawal_string = contents[25]
                print("Withdrawal String:", withdrawal_string)

                whitespace_index = withdrawal_string.index(" ")
                withdrawal_amount = withdrawal_string[
                    whitespace_index + 2 :
                ]  # plus 2 to move past the first whitespace and the dollar sign
                withdrawal_date = end_date

                print(
                    "Withdrawal date:", date_helper.conv_two_digit_date(withdrawal_date)
                )
                print("Withdrawal amount:", withdrawal_amount)
                transactions.append(
                    Transaction.Transaction(
                        withdrawal_date,
                        self.account_id,
                        None,
                        withdrawal_amount,
                        "WithdrawalsandOtherDebits",
                    )
                )  # order: date, account_id, category_id, amount, description

                pass
        except FileNotFoundError:
            gui_helper.gui_print(
                self.frame, self.prompt, "Uh oh, error in data loading"
            )
            gui_helper.alert_user(
                self.frame, "Missing data!", "You might be missing your marcus.pdf file"
            )
            return False

        return transactions
