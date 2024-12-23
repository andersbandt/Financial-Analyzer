"""
@file a06_balances.py
@brief CLI tab for managing balances of various accounts

"""

# import needed modules
import numpy as np

# import user CLI stuff
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined modules
import db.helpers as dbh
import analysis.analyzer_helper as anah
import analysis.balance_helper as balh
import analysis.investment_helper as invh
import analysis.graphing.graphing_analyzer as grapa
import tools.date_helper as dateh
from utils import log_helper as logh

# import logger
from loguru import logger


class TabBalances(SubMenu):
    def __init__(self, title, basefilepath):
        # initialize information about sub menu options
        action_arr = [Action("Show executive wealth summary", self.a01_show_wealth),
                      Action("Add balance", self.a02_add_balance),
                      Action("Graph balances per account", self.a03_graph_account_balance),
                      Action("Retirement modeling", self.a04_retirement_modeling),
                      Action("Delete a balance", self.a05_delete_balance),
                      Action("Print raw balance table", self.a06_print_balance_table),
                      Action("View asset allocation", self.a07_asset_allocation)]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    # a01_show_wealth: prints out tabular view of account balances (either from latest .db entry or live stock price)
    def a01_show_wealth(self):
        values_table = []  # values table to print
        total_value = 0
        for acc_id in dbh.account.get_all_account_ids():
            bal_amount, bal_date = balh.get_account_balance(acc_id)
            values_table.append([dbh.account.get_account_name_from_id(acc_id), bal_amount, bal_date])
            total_value += bal_amount

        clip.print_variable_table(
            ["Account Name", "Balance", "Updated Date"],
            values_table,
            format_finance_col=1
        )
        print(f"Total of all assets: ${total_value}")

    # a02_add_balance: inserts data for an account balance record into the SQL database
    def a02_add_balance(self):
        print("... adding a balance entry ...")

        # prompt user for account ID
        account_id = clih.account_prompt_all("What account do you want to add balance to?")
        if account_id is False or None:
            return False

        # prompt for balance amount
        bal_amount = clih.spinput("\nWhat is the amount for balance entry? (no $): ",
                                  inp_type="float")
        if bal_amount is False:
            return False

        # prompt user for date
        bal_date = clih.get_date_input("\nand what date is this balance record for?")
        if bal_date is False or bal_date is None:
            print("Ok, quitting add balance")
            return False

        # add balance
        status = balh.add_account_balance(account_id, bal_amount, bal_date)
        return status

    # a03_graph_account_balance: produces some graphs of account balances across time
    def a03_graph_account_balance(self):
        # set parameters
        # tag:HARDCODE
        days_previous = 560
        N = 5

        # clear tmp folder
        # TODO: how do I make this happen for all functions in a cli tab class?
        logh.clear_tmp_folder()

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

        # generate pdf file AND open
        # TODO: standardize this below process of generation and opening
        print("\nGenerating .pdf ...")
        image_folder = "tmp"
        output_pdf = "tmp/balances_summary.pdf"
        logh.generate_summary_pdf(image_folder, output_pdf)

    # ao4_retirement_modeling: performs some statistical analysis on likely-hood of retirement goals
    def a04_retirement_modeling(self):
        # SET UP estimates about timeline
        retirement_age = 59.5
        current_age = 25 # TODO: need to calculate current age based on input birthday here
        death_age = 95
        working_years_left = retirement_age - current_age
        years_retired = death_age - retirement_age

        # SET UP estimates about the economy
        annual_return = .06
        inflation_rate = 0.03
        real_annual_return = (1 + annual_return) / (1 + inflation_rate) - 1

        # RETRIEVE the CURRENT balance
        acc_id_arr, acc_balances = balh.get_retirement_balances()
        retirement_sum = 0
        for balance in acc_balances:
            retirement_sum += balance

        # CALCULATE the FUTURE balance
        # TODO: add some monte carlo modeling to determine different outcomes based on certain probabilities
        retirement_age_balance = retirement_sum * (1 + real_annual_return) ** working_years_left

        # CALCULATE how much you could take off principal monthly
        r = real_annual_return / 12  # monthly interest rate (adjusted for inflation)
        monthly_withdrawal = (retirement_age_balance * r) / (1 - pow((1 + r), -1 * 12 * years_retired))

        # PRINT out info for the user
        clip.print_variable_table(
            [dbh.account.get_account_name_from_id(x) for x in acc_id_arr],
            [["${:,.2f}".format(acc_bal) for acc_bal in acc_balances]],
            min_width=15,
            max_width=40,
            format_finance_col=None,
            add_row_numbers=False
        )
        logger.info("\nYou have this much saved in retirement specific accounts: " + "${:,.2f}".format(retirement_sum))
        logger.info(f"\nOk, so theoretically you only have {working_years_left} working years left.")
        logger.info(
            f"\nAt an annual return of {annual_return} (adjusted for {inflation_rate} inflation) for {working_years_left} years, you are estimated to have: {"${:,.2f}".format(retirement_age_balance)}"
        )
        logger.info(f"\nThis is based on a retirement age of {retirement_age}")
        logger.info(f"\nThis allows a dynamic monthly withdrawal strategy for {years_retired} years based on real return: {monthly_withdrawal}")
        logger.info(f"\nThis is also based on a death age of {death_age}")
        logger.info(f"\nor retired for {years_retired}")

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

    def a07_asset_allocation(self):
        # add liquid assets
        asset_total = {
            "CASH": balh.get_liquid_balance()
        }

        # add investment assets
        tickers = invh.get_all_active_ticker()
        for ticker in tickers:
            # keep pie chart clean by grouping similar categories. tag:HARDCODE
            if ticker.type == "MONEYMARKET":
                ticker.type = "CASH"

            # Add ticker value, initialize with 0 if the key does not exist
            asset_total[ticker.type] = asset_total.get(ticker.type, 0) + ticker.value

        # make pie plot
        grapa.create_pie_chart(
            asset_total.values(),
            asset_total.keys(),
            explode=0,
            title="Asset Allocation"
        )
        grapa.show_plots()
