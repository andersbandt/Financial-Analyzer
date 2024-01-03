# import needed packages
from pprint import pprint

# import user defined modules
import db.helpers as dbh
import analysis.analyzer_helper as anah
import analysis.balance_helper as balh
import analysis.graphing_analyzer as grapa

import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.tabs import SubMenu
import tools.date_helper as dateh

# import logger
from loguru import logger
from utils import logfn


# TODO: add some slots for tabular data
#   for example:
#       -latest balance record for each account along with date it was recorded on and type


class TabBalances(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        # initialize information about sub menu options
        action_strings = ["Show executive wealth summary",
                          "Add balance",
                          "Graph balances per account",
                          "Retirement modeling"]

        action_funcs = [self.a01_show_wealth,
                        self.a02_add_balance,
                        self.a03_graph_account_balance,
                        self.a04_retirement_modeling]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # a01_show_wealth
    def a01_show_wealth(self):
        acc_balances = []
        acc_dates = []
        acc_id_arr = dbh.account.get_all_account_ids()

        for acc_id in acc_id_arr:
            bal_amount, bal_date = balh.get_account_balance(acc_id)
            acc_balances.append(bal_amount)
            acc_dates.append(bal_date)

        # use cli_printer to print a table of balances
        clip.print_balances(
            [dbh.account.get_account_name_from_id(x) for x in acc_id_arr],
            acc_balances,
            "BALANCE SUMMARY"
        )

        print(acc_dates)

    # a02_add_balance: inserts data for an account balance record into the SQL database
    # TODO: add input for if the account is a retirement account or not
    def a02_add_balance(self):
        print("... adding a balance entry ...")

        # prompt user for account ID
        account_id = clih.account_prompt_all("What account do you want to add balance to?")

        # prompt for balance amount
        bal_amount = clih.spinput("\nWhat is the amount for balance entry? (no $): ",
                                  inp_type="float")

        # prompt user for date
        bal_date = clih.get_date_input("\nand what date is this balance record for?")
        if bal_date is False:
            print("Ok, quitting add balance")
            return False

        # add balance
        status = balh.add_account_balance(account_id, bal_amount, bal_date)
        return status

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

        # TODO: stacked line chart improvements. 1-sort account order by size? type?  2-
        grapa.create_stackline_chart(edge_code_date[1:],
                                     values_array,
                                     title=f"Balances per account since {edge_code_date[0]}",
                                     label=account_names_array,
                                     y_format='currency')

    # TODO: add some monte carlo modeling to determine different outcomes based on certain probabilities
    def a04_retirement_modeling(self):
        acc_id_arr, acc_balances = balh.produce_retirement_balances()

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


    def show_liquid_over_time(self):
        print("INFO: show_liquid_over_time running")

        # set params
        days_previous = 180  # half a year maybe?
        N = 5

        # get pyplot figure
        figure = graphing_analyzer.create_liquid_over_time(days_previous, N)

        # get data for displaying balances in tabular form
        spl_Bx = analyzer_helper.gen_Bx_matrix(days_previous, N)
        recent_Bx = spl_Bx[-1]

        print("Working with this for tabulated data conversion")
        print(recent_Bx)

    # def show_wealth_by_type(self):
    #     balance_by_type = []
    #
    #     # iterate across account types
    #     for acc_type in range(1, 4 + 1):
    #         acc_sum = 0
    #         acc_id_by_type = dbh.account.get_account_id_by_type(acc_type)
    #
    #         for acc_id in acc_id_by_type:
    #             print("Checking acc_id: " + str(acc_id))
    #             bal = dbh.balance.get_recent_balance(acc_id)
    #             print("Got balance of " + str(bal))
    #             acc_sum += bal
    #
    #         balance_by_type.append(acc_sum)
    #
    #     print("Here is your recent balance history by account type")
    #     print(balance_by_type)
