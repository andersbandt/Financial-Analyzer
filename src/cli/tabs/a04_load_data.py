"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import needed packages
import csv

# import user defined modules
import cli.cli_helper as clih
from categories import categories_helper
from cli.tabs import SubMenu
from tools import load_helper as loadh


class TabLoadData(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        self.statement = None

        self.basefilepath = basefilepath # had to add this in, at some point maybe delete?

        # initialize information about sub menu options
        action_strings = ["Load data", "Load ALL data", "Check data status"]
        action_funcs = [self.a01_load_data, self.a01b_load_all_data, self.a02_check_status]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    # def run(self):
    #     super().run()
    #     return self.statement

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

# I was feeling pretty high and weird writing below code so maybe give it an audit on efficacy
        try:
            [year, month] = clih.prompt_year_month()
        except TypeError:
            res = clih.promptYesNo("Bad date input. Try again?")
            if res:
                [year, month] = clih.prompt_year_month()
            else:
                return False

        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=False)

        print(f"\nCreating master Statement object for all files in date bin {year}-{month}")
        self.statement = loadh.create_master_statement(statement_list) # TODO: I think I should have this be a Statement instead of a Ledger
        self.statement.print_statement()

        print("Statement loaded successfully, can continue with load process")
        self.update_listing()
        return True


    def a01b_load_all_data(self):
        print("... loading in ALL financial data")

        statement_list = []

        year_range = ["2020", "2021", "2022", "2023"]

        for year in year_range:
            for month in range(1, 12+1):
                tmp_list = loadh.get_month_year_statement_list(self.basefilepath, year, month)
                statement_list.extend(tmp_list)

        print("\t... finished creating all Statement objects in range")

        print("\nCreating master Ledger object")
        self.statement = loadh.create_master_ledger(statement_list)

        print("\t... done creating Ledger object.\n Updating listings and exiting.")
        self.update_listing()


    def a02_check_status(self):
        print("... checking data status ...")


##### BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a03_categorize_statement(self):
        print("\n\na03: Automatically categorizing Statement")
        categories = categories_helper.load_categories()

        self.statement.categorizeLedgerAutomatic(categories)
        self.statement.print_statement()

        res = clih.promptYesNo("Do you want to attempt manual categorization of remaining transactions?")
        if res:

            self.statement.categorize_manual()
        else:
            print("Ok, leaving statement with just automatic categorization applied")


    # a04_print_statement_summary: prints a summary of the currently loaded statement
    # TODO: I think I can phase this function out? Probably just needed during program bringup?
    def a04_print_statement_summary(self):
        for statement in self.statement_list:
            print(statement.title)


    # a05_save_statement_csv: saves the currently loaded statement to a .csv file
    def a05_save_statement_csv(self):
        print("... saving statement to .csv")
        try:
            # open the file
            # utf-8-sig is used as it includes a Byte Order Mark that helps programs recognize the file as UTF-8
            with open('C:/Users/ander/Downloads/test.csv', 'w', encoding='utf-8-sig', newline='') as f:
                csv_writer = csv.writer(f)
                # csv_writer = csv.writer(f, dialect='excel-tab')

                # write headers
                csv_writer.writerow(["Date", "Amount", "Description", "Category", "Source"])

                # iterate through all transactions
                if self.statement.transactions is not None:
                    for transaction in self.statement.transactions:
                        string_dict = transaction.getStringDict()

                        # write the row
                        csv_writer.writerow([
                            string_dict['date'],
                            string_dict['amount'],
                            string_dict['description'],
                            string_dict['category'],
                            string_dict['source']])
        except Exception as e:
            print("Can't save statement: ", e)


    # a06_print_ledger: prints the currently loaded ledger
    def a06_print_ledger(self):
        print(" ... printing current Ledger object")
        self.statement.sort_date_desc()
        self.statement.print_statement()


    # a07_sort_ledger: sorts the ledger by some metric
    def a07_sort_ledger(self):
        print(" ... sorting Ledger object")
        # method = ["$ up", "$ down", "date up", "date down"]
        #  inp_auto(prompt, strings_arr, echo=True, stat=None)
        self.statement.sort_trans_asc()
        self.statement.print_statement()


    def a08_save_statement_db(self):
        print("... saving statement to .db file ...")
        self.statement.save_statement()

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################

# TODO: probably can migrate some of these functions into `load_helper.py`

    def update_listing(self):
        # append new actions to menu now that statement is loaded in
        self.action_strings.append("Categorize statement")
        self.action_strings.append("Statement summary")
        self.action_strings.append("Save to .csv")
        self.action_strings.append("Print new Ledger")
        self.action_strings.append("Sort ledger")
        self.action_strings.append("Save to database")
        self.action_funcs.append(self.a03_categorize_statement)
        self.action_funcs.append(self.a04_print_statement_summary)
        self.action_funcs.append(self.a05_save_statement_csv)
        self.action_funcs.append(self.a06_print_ledger)
        self.action_funcs.append(self.a07_sort_ledger)
        self.action_funcs.append(self.a08_save_statement_db)
        return True


    def categorize_automatic(self):
        pass



    # def a01_load_data(self):
    #     print("... loading in financial data ...")
    #
    #     status = True
    #     while status:
    #         def prompt_date():
    #             print("\n... prompting user to find file for Statement")
    #             # get date information to determine which folder to look in
    #             y = clih.get_year_input()
    #             m = clih.get_month_input()
    #             return [y, m]
    #
    #         [year, month] = prompt_date()
    #         if month == -1 or year == -1:
    #             res = clih.promptYesNo("Bad date input. Try again?")
    #             if res:
    #                 [year, month] = prompt_date()
    #
    #         # look in the folder to determine loaded files
    #         dir_path = clih.get_statement_folder(self.basefilepath, year, month)
    #         print("Looking at path: " + dir_path)
    #         dir_list = os.listdir(dir_path)
    #         if len(dir_list) == 0:
    #             print("Yikes! No files found")
    #         i = 0
    #         for file in dir_list:
    #             print(str(i+1) + ": " + file)
    #             i += 1
    #
    #         # get individual file
    #         file_sel = clih.spinput("Select what number file you want to load in (1 to N): ", type="int")
    #
    #         # STANDARD FLOW CONTROL FOR SPINPUT
    #         if file_sel == False:
    #             break
    #         elif file_sel == -1:
    #             status = False
    #             break
    #         # END OF FLOW CONTROL
    #
    #         file = dir_list[file_sel-1]
    #         print("\nYou selected " + file)
    #
    #         # create Statement object for file
    #         self.statement = loadh.create_statement(year, month, dir_path + file)
    #         self.statement.load_statement_data()
    #         self.statement.print_statement()
    #         print("Statement loaded successfully, can continue with load process")
    #         status = False
    #
    #     self.update_listing()
