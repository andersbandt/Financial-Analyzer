"""
@file a06_balances.py
@brief CLI tab for managing balances of various accounts

"""

# import needed modules
import numpy as np

# import user defined modules
import db.helpers as dbh
import analysis.analyzer_helper as anah
import analysis.balance_helper as balh

import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.tabs import SubMenu
import tools.date_helper as dateh

# import logger
from loguru import logger


class TabBalances(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        # initialize information about sub menu options
        action_strings = ["Show executive wealth summary",
                          "Add balance",
                          "Graph balances per account",
                          "Retirement modeling",
                          "Delete balance entries",
                          "Print .db balance"]

        action_funcs = [self.a01_show_wealth,
                        self.a02_add_balance,
                        self.a03_graph_account_balance,
                        self.a04_retirement_modeling,
                        self.a05_delete_balance,
                        self.a06_print_balance_table]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # a01_show_wealth: prints out tabular view of account balances (either from latest .db entry or live stock price)
    # TODO: possibly omit any accounts with a balance of 0 (and print out which accounts were omitted)
    def a01_show_wealth(self):
        values_table = []  # values table to print
        for acc_id in dbh.account.get_all_account_ids():
            bal_amount, bal_date = balh.get_account_balance(
                acc_id)  # TODO: let's audit this function and possibly add some hooks for options (live stock price, latest recorded, etc)
            values_table.append([dbh.account.get_account_name_from_id(acc_id), bal_amount, bal_date])

        clip.print_variable_table(
            ["Account id", "Amount", "Date"],
            values_table,
            format_finance_col=1
        )

    # a02_add_balance: inserts data for an account balance record into the SQL database
    def a02_add_balance(self):
        print("... adding a balance entry ...")

        # prompt user for account ID
        account_id = clih.account_prompt_all("What account do you want to add balance to?")
        if account_id is False:
            return False

        # prompt for balance amount
        bal_amount = clih.spinput("\nWhat is the amount for balance entry? (no $): ",
                                  inp_type="float")
        if bal_amount is False:
            return False

        # prompt user for date
        bal_date = clih.get_date_input("\nand what date is this balance record for?")
        if bal_date is False:
            print("Ok, quitting add balance")
            return False

        # add balance
        status = balh.add_account_balance(account_id, bal_amount, bal_date)
        return status

    # a03_graph_account_balance: produces some graphs of account balances across time
    def a03_graph_account_balance(self):
        print("... showing all liquid and investment assets ...")

        # set parameters
        days_previous = 560
        N = 5

        # generate matrix of Bx values
        spl_Bx, edge_code_date = anah.gen_Bx_matrix(
            dateh.get_cur_date(),
            days_previous,
            N)

        # error handling on amount of binning done to balances
        if len(spl_Bx) != N:
            logger.debug(f"Length of spl_Bx: {len(spl_Bx)}")
            logger.debug(f"N is:{str(N)}")

        account_id_array = list(spl_Bx[0].keys())
        account_names_array = [dbh.account.get_account_name_from_id(account_id) for account_id in account_id_array]
        values_array = [[a_A[account_id] for a_A in spl_Bx] for account_id in account_id_array]

        # TYPE 1:
        balh.graph_balance_1(edge_code_date, values_array, account_names_array)

        # TYPE 2: by account type
        balh.graph_balance_2(edge_code_date, values_array, account_id_array)

        # TYPE 3: using .db data to model day by day balance
        balance_history = balh.model_account_balance(2000000003)
        dates = [date for date, balance in balance_history]
        balances = [balance for date, balance in balance_history]
        balh.graph_balance_3(dates, balances)

    # TODO: add some monte carlo modeling to determine different outcomes based on certain probabilities
    def a04_retirement_modeling(self):
        acc_id_arr, acc_balances = balh.get_retirement_balances()

        # use cli_printer to print a table of balances
        clip.print_balances(
            [dbh.account.get_account_name_from_id(x) for x in acc_id_arr],
            acc_balances,
            "RETIREMENT ACCOUNT BALANCE SUMMARY"
        )

        # CALCULATE the current sum of retirement specific accounts
        retirement_sum = 0
        for balance in acc_balances:
            retirement_sum += balance

        print(f"\n\nYou have this much saved in retirement specific accounts: {retirement_sum}")

        # CALCULATE my account balance starting at age 59.5
        num_years = 59.5 - 24
        annual_return = .06
        inflation_rate = 0.03
        real_annual_return = (1 + annual_return) / (1 + inflation_rate) - 1

        retirement_age_balance = retirement_sum * (1 + real_annual_return) ** num_years
        print(
            f"\n\nAt an annual return of {annual_return} (adjusted for {inflation_rate} inflation) for {num_years} years, you are estimated to have: {retirement_age_balance}")

        # CALCULATE monthly withdrawal in retirement
        years_retired = 95 - 63
        r = real_annual_return / 12  # monthly interest rate (adjusted for inflation)
        monthly_withdrawal = (retirement_age_balance * r) / (1 - pow((1 + r), -1 * 12 * years_retired))
        print(
            f"\n\nThis allows a dynamic monthly withdrawal strategy for {years_retired} years based on real return: {monthly_withdrawal}")

    def a05_delete_balance(self):
        self.a06_print_balance_table()
        print("\nPlease enter the sql key of transactions you want to delete. Enter 'quit' or 'q' to finalize list")
        status = True
        sql_key_arr = []
        while status:
            sql_key = clih.spinput("\tsql_key: ", inp_type="int")
            if sql_key is False:
                status = False
            else:
                sql_key_arr.append(sql_key)
                print(sql_key_arr)

        # get one last user confirmation
        if len(sql_key_arr) == 0:
            print("Quitting balance delete!")

        print("\n\n== BALANCES TO DELETE ==")
        for sql_key in sql_key_arr:
            print(dbh.balance.get_balance(sql_key))
        print("\nGreat, planning on deleting the shown list of balances.")
        res = clih.promptYesNo("Is that ok?")
        if not res:
            return False

        # delete balances
        for sql_key in sql_key_arr:
            dbh.balance.delete_balance(sql_key)
        return True

    # a06_print_balance_table: prints all recorded .db balances
    def a06_print_balance_table(self):
        # retrieve ledger data as tuples and convert into 2D array
        balance_ledge = dbh.balance.get_balance_ledge_data()
        balance_arr = np.array(balance_ledge)

        # convert account ID to name
        for entry in balance_arr:
            entry[1] = dbh.account.get_account_name_from_id(entry[1])

        # use clip to print table
        clip.print_variable_table(
            ["SQL key", "Balance", "Account", "Date"],
            balance_arr,
            format_finance_col=2
        )
        return True
