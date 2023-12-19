"""
@file a09_investments.py
@brief sub menu for loading in raw financial data and storing in database


"""


# import user defined modules
import cli.cli_helper as clih
from cli.tabs import SubMenu
from analysis import investment_helper as invh
import db.helpers as dbh


class TabInvestment(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None

        # initialize information about sub menu options
        action_strings = ["Check investments",
                          "Add investment transaction",
                          "Check accounts summary"]

        action_funcs = [self.a01_check_investments,
                        self.a02_add_investment,
                        self.a03_check_accounts]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_check_investments(self):
        print("... checking investment data ...")
        return True


    def a02_add_investment(self):
        print("... adding investment transaction ...")

        # get account information
        account_id = clih.account_prompt_type("What is the corresponding account for this investment?: ", 4)

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


    def a03_check_accounts(self):
        print("... checking investment data for each account ...")

        inv_acc_id = dbh.account.get_account_id_by_type(4)

        acc_val_arr = []
        for account_id in inv_acc_id:
            account_value = invh.summarize_account(account_id, printmode=True)
            acc_str = dbh.account.get_account_name_from_id(account_id)
            acc_val_arr.append(account_value)
            # print(f"\t {acc_str}: {account_value}")

        for i in range(0, len(inv_acc_id)):
            acc_str = dbh.account.get_account_name_from_id(inv_acc_id[i])
            print(f"\t {acc_str}: {acc_val_arr[i]}")

        return True


    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################


