
# import needed modules
from prompt_toolkit import prompt
# from prompt_toolkit import print_formatted_text as print

# import needed packages

from cli.tabs import *

# from cli.tabs import a01_dashboard
# from cli.tabs import a02_analyze_history
# from cli.tabs import a03_categories
# from cli.tabs import a04_account
# from cli.tabs import a05_load_data
# from
# from cli.tabs import a09_investments


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
        self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials"

        # initialize the tabs in self.tabs[]
        self.initTabs()



    def setTabs(self):
        self.tabs = [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6, self.tab7, self.tab8, self.tab9]

    # set up tab control
    def initTabs(self):
        print("Creating tab nav bar and initializing tab content")

        self.tab1 = a01_dashboard.TabMainDashboard("Main Dash", self.basefilepath)
        self.tab2 = a02_categories.TabCategory("Manage Categories", self.basefilepath)
        self.tab3 = a03_account.TabAccount("Manage Accounts", self.basefilepath)
        self.tab4 = a04_load_data.TabLoadData("Load Data", self.basefilepath)
        self.tab5 = a05_analyze_history.TabSpendingHistory("Analyze Spending History", self.basefilepath)
        self.tab6 = a02_categories.TabCategory("Balances", self.basefilepath)
        self.tab7 = a07_categorize_transaction.TabTransCategorize("Categorize Transactions", self.basefilepath)
        self.tab8 = a02_categories.TabCategory("Budgeting", self.basefilepath)
        self.tab9 = a09_investments.TabInvestment("Review investments", self.basefilepath)

        self.setTabs()

        return True


    def print_header(self):
        print("\n\n\n")
        print("#############################################")
        print("############ MAIN PROGRAM ###################")
        print("#############################################")


    def mainloop(self):
        # print out menu options
        print("Attempting to start main loop of CLI interface menu")

        while True:
            self.print_header()

            i = 1
            for tab in self.tabs:
                if tab is not None:
                    print(str(i) + ": " + tab.title)
                    i = i + 1
                else:
                    print("NONE")
                    i = i + 1

            print("0: EXIT PROGRAM")

            # ask user for choice
            choice = input('Enter your choice: ')

            if choice == '0':
                print('Exiting...')
                break
            else:
                # convert input to INT
                try:
                    choice_int = int(choice)
                except ValueError:
                    print("Invalid integer string")

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