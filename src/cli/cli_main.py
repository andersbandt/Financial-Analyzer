

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
        self.tab10 = None

        self.tabs = []

        # tag:BASEFILEPATH
        self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials" # tag:hardcode

        # initialize the tabs in self.tabs[]
        self.initTabs()

    def setTabs(self):
        self.tabs = [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6, self.tab7, self.tab8, self.tab9, self.tab10]

    # set up tab control
    def initTabs(self):
        print("Creating tab nav bar and initializing tab content")

        self.tab1 = a01_dashboard.TabMainDashboard("Main Dash", self.basefilepath)
        self.tab2 = a02_categories.TabCategory("Manage Categories", self.basefilepath)
        self.tab3 = a03_account.TabAccount("Manage Accounts", self.basefilepath)
        self.tab4 = a04_load_data.TabLoadData("Load Data", self.basefilepath)
        self.tab5 = a05_analyze_history.TabSpendingHistory("Analyze Spending History", self.basefilepath)
        self.tab6 = a06_balances.TabBalances("Balances", self.basefilepath)
        self.tab7 = a07_categorize_transaction.TabTransCategorize("Categorize Transactions", self.basefilepath)
        self.tab8 = a02_categories.TabCategory("Budgeting", self.basefilepath)
        self.tab9 = a09_investments.TabInvestment("Review investments", self.basefilepath)
        self.tab10 = a10_plaid.TabPlaid("Plaid Integration", self.basefilepath)

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
def main(tab_num=None, action_num=None):
    """
    Main function of CLI interface.

    Args:
        tab_num: Optional tab number (1-9) to run directly
        action_num: Optional action number within the tab to run directly
    """
    print("Executing main function of CLI interface")

    # create main app
    app = MainApplication()

    # If tab and action specified, run directly
    if tab_num is not None and action_num is not None:
        # Validate tab number
        if tab_num < 1 or tab_num > len(app.tabs):
            print(f"Error: Tab {tab_num} is out of range (1-{len(app.tabs)})")
            return

        # Get the specified tab
        selected_tab = app.tabs[tab_num - 1]  # Convert to 0-indexed

        # Validate action number
        if action_num < 1 or action_num > len(selected_tab.action_arr):
            print(f"Error: Action {action_num} is out of range for tab '{selected_tab.title}' (1-{len(selected_tab.action_arr)})")
            print("\nAvailable actions:")
            for i, action in enumerate(selected_tab.action_arr, 1):
                print(f"  {i}: {action.title}")
            return

        # Run the specific action
        print(f"\n==> Running Tab {tab_num} ('{selected_tab.title}'), Action {action_num}")
        selected_tab.run_sub_action(action_num)
        print("\n==> Direct action completed")

    else:
        # Run interactive application
        app.mainloop()
