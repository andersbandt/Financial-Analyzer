
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
                          "Show stacked liquid investment"]

        action_funcs = [self.a01_show_wealth,
                        self.a02_add_balance,
                        self.a03_show_stacked_liquid_investment]


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

        # insert_category: inserts a category into the SQL database
        dbh.balance.insert_account_balance(account_id,
                                           bal_amount,
                                           bal_date)

        # print out balance addition confirmation
        print(f"Great, inserted a balance of {bal_amount} for account {account_id} on date {bal_date}")

        return True


    # this function will be interesting to write.
    # I think I should keep a cumulative total of two balances - checkings/savings and investments
    # Then as I iterate across dates everytime there is a new entry I update that total and make a new record
    def a03_show_stacked_liquid_investment(self):
        print("... showing all liquid and investment assets ...")

        # set parameters
        days_previous = 365
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
            # raise GraphingAnalyzerError(
            #     f"YOUR spl_Bx array is not of length N it is length {len(spl_Bx)}"
            # )

        print("\nspl_Bx matrix below\n")
        pprint(spl_Bx)

        print("\nEdge code date below")
        pprint(edge_code_date)

        account_id_array = []
        for key, values in spl_Bx[0].items():
            account_id_array.append(key)

        values_array = []
        for account_id in account_id_array:
            tmp_values = []
            for a_A in spl_Bx:
                tmp_values.append(a_A[account_id])
            # for key, value in a_A.items():
            #     account_id_array.append(key)
            #     tmp_values.append(value)
            values_array.append(tmp_values)

        print("Keys:", account_id_array)
        print("Values:", values_array)

        grapa.create_mul_line_chart(edge_code_date[1:],
                                    values_array,
                                    title=None,
                                    labels=account_id_array,
                                    y_format='currency')



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



