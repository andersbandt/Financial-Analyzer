"""
@file a09_investments.py
@brief sub menu for loading in raw financial data and storing in database


"""

# import needed modules
import datetime
from pprint import pprint

# import user CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined modules
from analysis import investment_helper as invh
from analysis.data_recall import transaction_recall as trans
import analysis.graphing_analyzer as grapa
from tools import date_helper as dateh
import db.helpers as dbh


# TODO: let's create a function to calculate the "health" of my investment.ledger calculated account balances vs my manual entry ones
#   have a limit on like the past 3 days the actual balance one has to be entered


class TabInvestment(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [Action("Check investments", self.a01_check_investments),
                      # Action("Print investment database", self.a02_print_db_inv),
                      Action("Add investment transaction", self.a03_add_investment),
                      Action("Check account balances/summary", self.a04_check_accounts),
                      Action("Show current value snapshot history", self.a05_cur_value_history),
                      Action("Add investment balance", self.a06_add_inv_balances)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_check_investments(self):
        print("... checking investment data ...")
        print("Anders you gotta finish this function!")
        return True

# TODO: finish this function to print investment transactions
    def a02_print_db_inv(self):
        # METHOD 1: cheap
        ledge_data = dbh.investments.get_investment_ledge_data()
        pprint(ledge_data)

        # METHOD 2: actuallyy doing it right
        transactions = transr.recall_transaction_data() # TODO: need to finish a function to recall InvestmentTransaction data. But where to put?
        tmp_ledger = Ledger.Ledger("All Investment Data")
        tmp_ledger.set_statement_data(transactions)
        tmp_ledger.print_statement()

    def a03_add_investment(self):
        print("... adding investment transaction ...")

        # get account information
        account_id = clih.account_prompt_type("What is the corresponding account for this investment?: ", 4)
        if account_id is False:
            print("... exiting add investment")
            return

        # get ticker information
        ticker = clih.spinput("\nWhat is the ticker of this investment?: ", inp_type="text")
        if ticker is False:
            print("... exiting add investment")
            return

        # do some checking on validity of ticker
        ticker_valid = invh.validate_ticker(ticker)
        if ticker_valid is False:
            res = clih.promptYesNo("\nSeems like ticker is not validated. Do you want to continue with entry?")
            if not res:
                print("Ok. Cancelling adding investment")
                return

        # TODO: buy and sell is not properly being recorded
        # check if InvestmentTransaction is a buy or sell
        buy_sell_int = clih.spinput("\nIs this a buy or sell? \t(1 for buy, 2 for sell): ", inp_type="int")
        if buy_sell_int is False:
            print("... exiting add investment")
            return

        inv_type = ""
        if buy_sell_int == 1:
            inv_type = "BUY"
        elif buy_sell_int == 2:
            inv_type == "SELL"
        else:
            print("Fuck man you entered something other than 1 or 2. I gotta quit now.")
            return False

        # get the number of shares
        shares = clih.spinput("What is the number of shares of this investment?: ", inp_type="float")
        if shares is False:
            print("... exiting add investment")
            return

        # get investment value at time of buy/sell
        value = clih.spinput("What was the value of this investment for this transaction?: ", inp_type="float")
        if value is False:
            print("... exiting add investment")
            return

        # get investment date
        date = clih.get_date_input("What is the date of this investment transaction?: ")
        if date is False:
            print("... exiting add investment")
            return

        # add note (OPTIONAL)
        res = clih.promptYesNo("Do you want to add a note?")
        if res:
            note = clih.spinput("What is the note for this investment transaction? \tnote: ", inp_type="text")
            if note is False:
                print("... exiting add investment")
                return
        else:
            note = None

        # insert the investment into the database
        dbh.investments.insert_investment(date,
                                          account_id,
                                          ticker,
                                          shares,
                                          inv_type,
                                          value,
                                          note=note)

    def a04_check_accounts(self):
        print("... checking investment data for each account ...")

        # populate array of accounts with type=4
        inv_acc_id = dbh.account.get_account_id_by_type(4)

        # populate arrays
        values = []
        for account_id in inv_acc_id:
            acc_val = invh.summarize_account(account_id, printmode=True)
            acc_str = dbh.account.get_account_name_from_id(account_id)
            values.append([acc_str, acc_val])

        # use cli_printer to pretty print balances
        print("\n... finished getting account info.\n")
        clip.print_variable_table(
            ["Account Name", "Value"],
            values,
            format_finance_col=1
        )
        return True

    def a05_cur_value_history(self):
        print("... summarizing value history ...")

        # set some parameters and populate my "active" investment data
        days_prev = 1000
        interval = "1d"
        act_inv_dict = invh.create_active_investment_dict()

        # populate dummy totals and dates
        # total_arr = list(range(days_prev))
        total_arr = []
        date_arr = []
        dummy_ticker_price_data = invh.get_ticker_price_data("AAPL",
                                                             dateh.get_date_previous(days_prev),
                                                             datetime.datetime.now(),
                                                             interval)

        for ticker_date_entry in dummy_ticker_price_data["date"]:
            date_arr.append(ticker_date_entry)
            total_arr.append(0)

        # iterate through all ticker entries in my deemed "active" summary
        for entry in act_inv_dict:
            print("\n")
            print(entry)

            price_data = invh.get_ticker_price_data(entry["ticker"],
                                                    dateh.get_date_previous(days_prev),
                                                    datetime.datetime.now(),
                                                    interval,
                                                    filter_weekdays=False)

            # print out the raw historical price data
            # print(type(price_data))
            # for date in price_data["date"]:
            #     print(date)

            # for i in range(0, len(cur_data)):
            #     if cur_data[i] != prev_data[i]:
            #         print(f"\nMISMATCH BELOW!")
            #         print(f"\n{cur_data[i]} != {prev_data[i]}")

            # do some verification of the length
            if len(price_data["close"]) != len(total_arr):
                print("Can't add current data because there is a mismatch in total dates")
                continue

            i = 0  # in this context i represents the dates
            for price in price_data["close"]:
                shares = entry["shares"]
                total_arr[i] += entry["shares"] * price
                i += 1

        print(date_arr)
        print(total_arr)

        grapa.create_line_chart(date_arr,
                                total_arr,
                                title="Historical price data of portfolio snapshot",
                                y_format='currency')

        print("Done running a04_cur_value_history with days previous of: ", days_prev)

    def a06_add_inv_balances(self):
        print("... adding investment balances to financials database ...")
        # populate array of accounts with type=4
        inv_acc_id = dbh.account.get_account_id_by_type(4)
        # populate arrays
        acc_val_arr = []
        for account_id in inv_acc_id:
            acc_val = invh.summarize_account(account_id, printmode=True)
            acc_val_arr.append(acc_val)

        # do one last check
        res = clih.promptYesNo(
            "Are you sure you want to add these investment account balances to the financial database?")
        if res:
            # add balances
            bal_date = dateh.get_cur_str_date()
            for i in range(0, len(inv_acc_id)):
                # insert_category: inserts a category into the SQL database
                dbh.balance.insert_account_balance(inv_acc_id[i],
                                                   acc_val_arr[i],
                                                   bal_date)

                # print out balance addition confirmation
                print(f"Great, inserted a balance of {acc_val_arr[i]} for account {inv_acc_id[i]} on date {bal_date}")

    def a07_add_dividend(self):
        print("... adding dividend for a ticker ...")
        # get account information
        account_id = clih.account_prompt_type("What is the corresponding account for this investment dividend?: ", 4)
        if account_id is False:
            print("... exiting add dividend.")
            return

        # get ticker information
        ticker = clih.spinput("\nWhat is the ticker of this investment dividend?: ", inp_type="text")
        if ticker is False:
            print("... exiting add dividend.")
            return

        # do some checking on validity of ticker
        ticker_valid = invh.validate_ticker(ticker)
        if ticker_valid is False:
            res = clih.promptYesNo("\nSeems like ticker is not validated. Do you want to continue with entry?")
            if not res:
                print("... exiting add dividend.")
                return

        # get the TOTAL number of shares CURRENTLY owned
        total_shares = clih.spinput("What is the TOTAL number of shares currently owned?: ", inp_type="float")
        if total_shares is False:
            print("... exiting add investment")
            return

        # perform some calculation on (current_total - recorded_total) to get dividend amount to add
        recorded_total = dbh.investments.get_ticker_shares(account_id, ticker)
        print(recorded_total)
        dividend_shares = total_shares - recorded_total

        # add note (OPTIONAL)
        res = clih.promptYesNo("Do you want to add a note?")
        if res:
            note = clih.spinput("What is the note for this investment transaction? \tnote: ", inp_type="text")
            if note is False:
                print("... exiting add investment")
                return
        else:
            note = None

        print(f"\nAdding {dividend_shares} to current {recorded_total} to reach a total of {total_shares}")
        print(f"Doing this for ticker {ticker}")
        res = clih.promptYesNo("Does all seem to checkout? Proceed with add?")
        if not res:
            return False
        # insert the investment into the database
        today_date = dateh.get_cur_str_date()
        dbh.investments.insert_investment(today_date,
                                          account_id,
                                          ticker,
                                          dividend_shares,
                                          "DIV",
                                          0.00,
                                          description=f"DIVIDEND: {dividend_shares}",
                                          note=note)
        return True

