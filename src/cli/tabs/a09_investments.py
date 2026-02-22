"""
@file a09_investments.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import needed modules
import datetime

# import user CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined modules
from statement_types.Ledger import Ledger
from account import account_helper as acch
from analysis import investment_helper as invh
from analysis.data_recall import transaction_recall as transr
import analysis.graphing.graphing_analyzer as grapa
from tools import date_helper as dateh
import db.helpers as dbh


class TabInvestment(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_arr = [Action("Check investments", self.a01_check_investments),
                      Action("Print investment database", self.a02_print_db_inv),
                      Action("Add investment transaction", self.a03_add_investment),
                      Action("Show current value snapshot history", self.a04_cur_value_history),
                      Action("Add snapshot of live investment balances to database", self.a05_add_inv_balances),
                      Action("Add dividend", self.a06_add_dividend),
                      Action("Delete investment", self.a07_delete_investment),
                      Action("Ticker investigation", self.a08_check_ticker),
                      Action("Populate ticker metadata (one-time setup)", self.a09_populate_ticker_metadata),
                      Action("Print ticker metadata", self.a10_print_ticker_metadata),
                      Action("Edit ticker asset type", self.a11_edit_ticker_metadata),
                      Action("DEBUG", self.a99_debug)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_check_investments(self):
        print("... checking investment data for each account ...")

        # populate array of accounts with type=4
        inv_acc_id = acch.get_account_id_by_type(4)

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

    def a02_print_db_inv(self):
        """Print all investment transactions with investment-specific columns using prettytable."""
        # Note: answering yes uses _PRICE_CACHE so repeat calls within a session are instant
        live_price = clih.promptYesNo("Do you want to get live price?")

        transactions = transr.recall_investment_transaction(live_price)

        if not transactions or len(transactions) == 0:
            print("No investment transactions to display")
            return

        # Build table headers
        headers = ["DATE", "TICKER", "TYPE", "SHARES", "STRIKE", "CUR PRICE", "GAIN %", "CAGR %", "ORIG VALUE", "VALUE", "ACCOUNT", "NOTE"]

        # Build rows of data
        values = []
        for inv_trans in transactions:
            # Get calculated values
            if live_price:
                current_price = inv_trans.get_price()
                gain_percent = inv_trans.get_gain()
                current_value = inv_trans.shares * current_price
            else:
                current_price = 0
                gain_percent = 0
                current_value = 0
            account_name = dbh.account.get_account_name_from_id(inv_trans.account_id)

            # CAGR: compound annual growth rate from purchase date to today
            cagr = 0
            if live_price and current_price > 0 and inv_trans.strike_price > 0:
                try:
                    purchase_date = datetime.datetime.strptime(inv_trans.date, "%Y-%m-%d").date()
                    years_held = (datetime.date.today() - purchase_date).days / 365.25
                    if years_held > 0:
                        cagr = ((current_price / inv_trans.strike_price) ** (1 / years_held) - 1) * 100
                except (ValueError, ZeroDivisionError):
                    cagr = 0

            orig_value = inv_trans.strike_price * inv_trans.shares

            row = [
                inv_trans.date,
                inv_trans.ticker,
                inv_trans.trans_type,
                f"{inv_trans.shares:.4f}",
                f"${inv_trans.strike_price:.2f}",
                f"${current_price:.2f}",
                f"{gain_percent:.2f}%",
                f"{cagr:.2f}%" if live_price else "N/A",
                f"${orig_value:.2f}",
                f"${current_value:.2f}",
                account_name,
                inv_trans.note if inv_trans.note else ""
            ]
            values.append(row)

        # Sort rows - prompt user for sort preference
        sort_options = {"1": ("DATE", 0), "2": ("TICKER", 1), "3": ("VALUE", 9)}
        print("Sort by: 1=Date  2=Ticker  3=Value")
        sort_choice = input("Sort choice (default=1): ").strip() or "1"
        sort_label, sort_col = sort_options.get(sort_choice, ("DATE", 0))
        values.sort(key=lambda r: r[sort_col])

        # Use the existing generic print_variable_table from cli_printer
        clip.print_variable_table(
            headers,
            values,
            min_width=10,
            max_width=50,
            format_finance_col=None,  # Already formatted in the data
            add_row_numbers=False,
            title="All Investment Data"
        )

    def a03_add_investment(self):
        print("... adding investment transaction ...")

        # get account information
        account_id = clih.account_prompt_type("What is the corresponding account for this investment?: ", 4)
        if account_id is False:
            print("... exiting add investment")
            return False

        # get ticker information
        ticker = clih.spinput("\nWhat is the ticker of this investment?: ", inp_type="text")
        if ticker is False:
            print("... exiting add investment")
            return False

        # do some checking on validity of ticker
        ticker_valid = invh.validate_ticker(ticker)
        if ticker_valid is False:
            res = clih.promptYesNo("\nSeems like ticker is not validated. Do you want to continue with entry?")
            if not res:
                print("Ok. Cancelling adding investment")
                return False

        # if ticker is not a Money Market ticker, check if they want to add opposite buy/sell event
        if not ticker == invh.get_account_mm_ticker(account_id):
            is_mm_trans = False
            mm_trans = clih.promptYesNo("Do you want to add an equal and opposite money market SELL/BUY event?")
        else:
            is_mm_trans = True
            mm_trans = False

        # check if InvestmentTransaction is a buy or sell
        buy_sell_int = clih.spinput("\nIs this a buy or sell? \t(1 for buy, 2 for sell): ", inp_type="int")

        if buy_sell_int == 1:
            inv_type = "BUY"
        elif buy_sell_int == 2:
            inv_type = "SELL"
        else:
            print("FUCK you entered something other than 1 or 2. I gotta quit now.")
            return False

        if is_mm_trans:
            # Money market: 1 share = $1, so just ask for dollar value and derive shares
            value = clih.spinput("What is the dollar value of this money market transaction?: ", inp_type="float")
            if value is False:
                print("... exiting add investment")
                return False
            shares = value
        else:
            # get the number of shares
            shares = clih.spinput("What is the number of shares of this investment?: ", inp_type="float")
            if shares is False:
                print("... exiting add investment")
                return False

            # get investment value at time of buy/sell
            value = clih.spinput("What was the value of this investment for this transaction?: ", inp_type="float")
            if value is False:
                print("... exiting add investment")
                return False

        # get investment date
        date = clih.get_date_input("What is the date of this investment transaction?: ")
        if date is False:
            print("... exiting add investment")
            return False

        # add note
        note = clih.spinput("What is the note for this investment transaction? \tnote: ", inp_type="text")
        if note is False:
            print("... exiting add investment")
            return False

        # insert the investment into the database
        dbh.investments.insert_investment(date,
                                          account_id,
                                          ticker,
                                          shares,
                                          inv_type,
                                          value,
                                          note=note)

        # insert money market transfer
        if mm_trans:
            mm_ticker = invh.get_account_mm_ticker(account_id)
            if inv_type == "BUY":
                mm_type = "SELL"
            elif inv_type == "SELL":
                mm_type = "BUY"

            dbh.investments.insert_investment(date,
                                              account_id,
                                              mm_ticker,
                                              value,
                                              mm_type,
                                              value,
                                              note="automatically added money market transaction")

        return True

    def a04_cur_value_history(self):
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

    def a05_add_inv_balances(self):
        print("... adding investment balances to financials database ...")
        # populate array of accounts with type=4
        inv_acc_id = acch.get_account_id_by_type(4)
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

    def a06_add_dividend(self):
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
        else:
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
        recorded_total = invh.get_account_ticker_shares(account_id, ticker)
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

    def a07_delete_investment(self):
        self.a02_print_db_inv()
        clih.action_on_int_array("Please enter SQL key of investments you want to delete",
                                 None,
                                 invh.delete_investment_list)
        return True

    def a08_check_ticker(self):
        ticker = clih.spinput("What is the ticker you want to look at?: ", "text")
        invh.ticker_info_dump(ticker)
        price = invh.get_ticker_price(ticker)
        print(f"Price: {price}")

    def a09_populate_ticker_metadata(self):
        """One-time setup to populate ticker metadata from investment history."""
        print("\n⚠️  This will fetch asset types for all tickers in your investment history.")
        print("This is a ONE-TIME setup that makes future operations much faster.\n")

        confirm = clih.promptYesNo("Continue?")
        if not confirm:
            print("Cancelled.")
            return False

        invh.populate_ticker_metadata_from_investments(delay_between_tickers=1.0)
        return True

    def a10_print_ticker_metadata(self):
        """Print the ticker metadata table."""
        invh.print_ticker_metadata_table()
        return True

    def a11_edit_ticker_metadata(self):
        """Manually set the asset type for a ticker in the metadata table."""
        invh.print_ticker_metadata_table()

        ticker = clih.spinput("\nEnter ticker to edit: ", inp_type="text")
        if ticker is False:
            return False
        ticker = ticker.upper().strip()

        # Show current classification
        current = dbh.ticker_metadata.get_ticker_metadata(ticker)
        if current:
            print(f"\nCurrent classification for {ticker}: {current[1]}")
        else:
            print(f"\n{ticker} not yet in metadata — will be added.")

        # Show valid options
        valid_types = ["EQUITY", "ETF", "MUTUALFUND", "BOND", "MONEYMARKET", "UNKNOWN"]
        print("\nValid asset types:")
        for i, t in enumerate(valid_types, 1):
            print(f"  {i}. {t}")

        choice = clih.spinput("Enter number or type a custom value: ", inp_type="text")
        if choice is False:
            return False
        try:
            new_type = valid_types[int(choice) - 1]
        except (ValueError, IndexError):
            new_type = choice.upper().strip()

        print(f"\nSetting {ticker} → {new_type}")
        if not clih.promptYesNo("Confirm?"):
            print("Cancelled.")
            return False

        invh.update_ticker_asset_type(ticker, new_type)
        print(f"Updated {ticker} → {new_type}")
        return True

    def a99_debug(self):
        account_id = "2000000005"
        ticker = invh.get_account_mm_ticker(account_id)
        print(f"Money Market Fund Ticker: {ticker}" if ticker else "Ticker not found.")
