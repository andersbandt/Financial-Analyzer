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
                      Action("Graph executive summary", self.a03_graph_account_balance),
                      Action("Retirement modeling", self.a04_retirement_modeling),
                      Action("Delete a balance", self.a05_delete_balance),
                      Action("Print raw balance table", self.a06_print_balance_table),
                      Action("View asset allocation", self.a07_asset_allocation),
                      Action("Graph single account balance", self.a08_graph_single_account_balance)]

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
        print("\nGenerating .pdf ...")
        logh.generate_summary_pdf("balance_graphs.pdf")

    # a04_retirement_modeling: performs some statistical analysis on likely-hood of retirement goals
    def a04_retirement_modeling(self, num_simulations=10000):
        # SET UP estimates about timeline
        retirement_age = 59.5
        current_age = 25
        death_age = 95
        working_years_left = retirement_age - current_age
        years_retired = death_age - retirement_age

        # SET UP estimates about the economy
        annual_return_mean = 0.06
        annual_return_stddev = 0.02  # standard deviation of annual returns
        inflation_mean = 0.03
        inflation_stddev = 0.01  # standard deviation of inflation rates

        # RETRIEVE the CURRENT balance
        acc_id_arr, acc_balances = balh.get_retirement_balances()
        retirement_sum = sum(acc_balances)

        # MONTE CARLO SIMULATION
        retirement_balances = []
        monthly_withdrawals = []

        for _ in range(num_simulations):
            # Simulate annual returns and inflation rates for working years
            simulated_returns = np.random.normal(annual_return_mean, annual_return_stddev, int(working_years_left))
            simulated_inflation = np.random.normal(inflation_mean, inflation_stddev, int(working_years_left))
            simulated_real_returns = [(1 + r) / (1 + i) - 1 for r, i in zip(simulated_returns, simulated_inflation)]

            # Calculate balance at retirement
            future_balance = retirement_sum
            for real_return in simulated_real_returns:
                future_balance *= (1 + real_return)
            retirement_balances.append(future_balance)

            # Simulate annual returns and inflation rates for retirement years
            simulated_returns_retired = np.random.normal(annual_return_mean, annual_return_stddev, int(years_retired))
            simulated_inflation_retired = np.random.normal(inflation_mean, inflation_stddev, int(years_retired))
            simulated_real_returns_retired = [(1 + r) / (1 + i) - 1 for r, i in
                                              zip(simulated_returns_retired, simulated_inflation_retired)]

            # Calculate monthly withdrawal using annuity formula
            avg_real_return_retired = np.mean(simulated_real_returns_retired)
            r = avg_real_return_retired / 12
            if r != 0:
                monthly_withdrawal = (future_balance * r) / (1 - pow(1 + r, -1 * 12 * years_retired))
            else:
                monthly_withdrawal = future_balance / (12 * years_retired)  # fallback for zero return
            monthly_withdrawals.append(monthly_withdrawal)

        # ANALYZE RESULTS
        balance_percentiles = np.percentile(retirement_balances, [10, 50, 90])  # 10th, 50th, 90th percentiles
        withdrawal_percentiles = np.percentile(monthly_withdrawals, [10, 50, 90])

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
        logger.info(f"\nMonte Carlo Results for Retirement Balance:")
        logger.info(f"  - 10th Percentile (Worst Case): ${balance_percentiles[0]:,.2f}")
        logger.info(f"  - 50th Percentile (Median Case): ${balance_percentiles[1]:,.2f}")
        logger.info(f"  - 90th Percentile (Best Case): ${balance_percentiles[2]:,.2f}")
        logger.info(f"\nMonte Carlo Results for Monthly Withdrawal:")
        logger.info(f"  - 10th Percentile (Worst Case): ${withdrawal_percentiles[0]:,.2f}")
        logger.info(f"  - 50th Percentile (Median Case): ${withdrawal_percentiles[1]:,.2f}")
        logger.info(f"  - 90th Percentile (Best Case): ${withdrawal_percentiles[2]:,.2f}")

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

    # a06_print_balance_table: prints recorded .db balances (all accounts or a specific one)
    def a06_print_balance_table(self, account_id=None):
        # prompt user to filter by account if not already specified
        if account_id is None:
            show_all = clih.promptYesNo("Show all accounts?")
            if not show_all:
                account_id = clih.account_prompt_all("Which account?")
                if account_id is False or account_id is None:
                    return False

        # retrieve balance data
        if account_id is not None:
            balance_ledge = dbh.balance.get_balance_by_account_id(account_id)
        else:
            balance_ledge = dbh.balance.get_balance_ledge_data()

        if len(balance_ledge) == 0:
            print("No balance records found.")
            return True

        balance_arr = np.array(balance_ledge)

        # convert account ID to name
        for entry in balance_arr:
            entry[1] = dbh.account.get_account_name_from_id(entry[1])

        # use clip to print table
        clip.print_variable_table(
            ["SQL key", "Balance", "Account", "Date"],
            balance_arr.tolist(),
            format_finance_col=2
        )
        return True

    def a07_asset_allocation(self):
        # Track detailed breakdown by asset type and account
        asset_breakdown = {}  # {asset_type: [(account_name, amount), ...]}
        asset_total = {}      # {asset_type: total_amount}

        # Add liquid cash assets (bank accounts, checking, savings, etc.)
        liquid_balance = balh.get_liquid_balance()
        asset_total["CASH"] = liquid_balance
        asset_breakdown["CASH"] = [("Liquid Accounts", liquid_balance)]

        # Track money market separately for CASH breakdown
        money_market_total = 0
        money_market_accounts = []

        # Add investment assets (with live prices and rate limiting)
        print("Fetching live investment prices (this may take a moment)...")
        tickers = invh.get_all_active_ticker(live_price=True, delay_between_tickers=0.2)

        for ticker in tickers:
            account_name = dbh.account.get_account_name_from_id(ticker.account_id)
            original_type = ticker.type

            # Handle None asset type (fallback to UNKNOWN)
            if ticker.type is None:
                ticker.type = "UNKNOWN"

            # Track money market separately before merging into CASH
            if ticker.type == "MONEYMARKET":
                money_market_total += ticker.value
                money_market_accounts.append((account_name, ticker.ticker, ticker.value))
                ticker.type = "CASH"  # Merge into CASH for pie chart

            # Add to totals
            asset_total[ticker.type] = asset_total.get(ticker.type, 0) + ticker.value

            # Add to breakdown
            if ticker.type not in asset_breakdown:
                asset_breakdown[ticker.type] = []
            asset_breakdown[ticker.type].append((account_name, ticker.ticker, ticker.value))

        # Print detailed breakdown
        print("\n" + "="*80)
        print("ASSET ALLOCATION BREAKDOWN")
        print("="*80)

        for asset_type in sorted(asset_total.keys()):
            print(f"\n{asset_type}: ${asset_total[asset_type]:,.2f}")
            print("-" * 60)

            if asset_type == "CASH":
                # Special handling for CASH - show liquid vs money market
                print(f"  Liquid Accounts:        ${liquid_balance:,.2f}")
                if money_market_total > 0:
                    print(f"  Money Market Funds:     ${money_market_total:,.2f}")
                    for acc_name, ticker, amount in money_market_accounts:
                        print(f"    • {acc_name:30s} ({ticker:6s})  ${amount:>12,.2f}")
            else:
                # Group by account and show tickers
                account_groups = {}
                for item in asset_breakdown[asset_type]:
                    if len(item) == 3:  # (account_name, ticker, value)
                        acc_name, ticker, value = item
                        if acc_name not in account_groups:
                            account_groups[acc_name] = []
                        account_groups[acc_name].append((ticker, value))

                for acc_name, holdings in sorted(account_groups.items()):
                    acc_total = sum(val for _, val in holdings)
                    print(f"  {acc_name:40s}  ${acc_total:>12,.2f}")
                    for ticker, value in holdings:
                        print(f"    • {ticker:10s}  ${value:>12,.2f}")

        # Print summary totals
        print("\n" + "="*80)
        print(f"TOTAL NET WORTH: ${sum(asset_total.values()):,.2f}")
        print("="*80 + "\n")

        # Make pie plot
        grapa.create_pie_chart(
            asset_total.values(),
            asset_total.keys(),
            explode=0,
            title="Asset Allocation"
        )
        grapa.show_plots()

    def a08_graph_single_account_balance(self):
        account_id = clih.account_prompt_all("Which account do you want to graph?")
        if account_id is False or account_id is None:
            return False

        account_name = dbh.account.get_account_name_from_id(account_id)

        # Try modeled day-by-day balance (works for accounts with transactions)
        balance_history = balh.model_account_balance(account_id)
        if balance_history:
            dates = [date for date, balance in balance_history]
            balances = [balance for date, balance in balance_history]
        else:
            # Fall back to raw balance snapshots (investment accounts, etc.)
            raw = dbh.balance.get_balance_by_account_id(account_id)
            if not raw:
                print("No balance data found for that account.")
                return False
            dates = [entry[3] for entry in raw]
            balances = [entry[2] for entry in raw]

        grapa.create_line_chart(dates, balances, title=f"Balance Over Time: {account_name}", y_format='currency', rotate_xticks=True)
        grapa.show_plots()
        return True
