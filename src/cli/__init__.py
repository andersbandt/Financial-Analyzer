

# import user defined modules
from cli.tabs import *


class MainApplication:
    def __init__(self, *args, **kwargs):
        self.tab1 = None
        self.tab2 = None
        self.tab3 = None
        self.tab4 = None
        self.tab5 = None
        self.tab6 = None
        self.tab7 = None
        self.tab8 = None
        self.tab9 = None

        self.tabs = []

        # tag:BASEFILEPATH
        self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials" # tag:hardcode

        # initialize the tabs in self.tabs[]
        self.initTabs()

    def setTabs(self):
        # TODO: below code is quite bad
        self.tabs = [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6, self.tab7, self.tab8, self.tab9]

    # set up tab control
    def initTabs(self):
        print("Creating tab nav bar and initializing tab content")

        # TODO: perform some refactor of my base file path
        #   1 - global variables (don't need to pass in for each Tab)
        #   2 - multiple paths. Input data source path vs. output path?
        self.tab1 = a01_dashboard.TabMainDashboard("Main Dash", self.basefilepath)
        self.tab2 = a02_categories.TabCategory("Manage Categories", self.basefilepath)
        self.tab3 = a03_account.TabAccount("Manage Accounts", self.basefilepath)
        self.tab4 = a04_load_data.TabLoadData("Load Data", self.basefilepath)
        self.tab5 = a05_analyze_history.TabSpendingHistory("Analyze Spending History", self.basefilepath)
        self.tab6 = a06_balances.TabBalances("Balances", self.basefilepath)
        self.tab7 = a07_categorize_transaction.TabTransCategorize("Categorize Transactions", self.basefilepath)
        self.tab8 = a02_categories.TabCategory("Budgeting", self.basefilepath)
        self.tab9 = a09_investments.TabInvestment("Review investments", self.basefilepath)

        self.setTabs()
        print("Tabs should be initialized")
        return True

    def print_header(self):
        print("\n\n")
        print("#############################################")
        print("############ MAIN PROGRAM ###################")
        print("#############################################")

    def mainloop(self):
        # print out menu options
        print("Attempting to start main loop of CLI interface menu")

        while True:
            error_flags = 0
            self.print_header()

            i = 1
            for tab in self.tabs:
                print(str(i) + ": " + tab.title)
                i = i + 1
            print("0: EXIT PROGRAM")

            # ask user for choice
            choice = input('Enter your choice: ')

            if choice == '0':
                print('Exiting...')
                break
            else:
                try:
                    choice_int = int(choice) # convert input to INT
                except ValueError:
                    print("\n\nInvalid integer string")
                    error_flags = 1
                if choice_int > len(self.tabs):
                    print("\n\n!!! List choice out of range !!!")
                    error_flags = 1

                # if no errors can run SubMenu
                if error_flags == 0:
                    self.tabs[choice_int-1].run()


###########################################################
######################### MAIN ############################
###########################################################

# main function
def main():
    print("Executing main function of CLI interface")

    # place main app
    app = MainApplication()

    # run application
    app.mainloop()
