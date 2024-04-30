
# import needed packages
import sqlite3

# import user defined modules
from db import DATABASE_DIRECTORY
from db import helpers as dbh
from cli.tabs import SubMenu


class TabMainDashboard(SubMenu.SubMenu):
    def __init__(self, title, basefilepath):

        # initialize information about sub menu options
        action_strings = ["High level summary",
                          "System configuration",
                          "Execute RAW SQL statement",
                          "TEST METHOD"]

        action_funcs = [self.a01_summary,
                        self.a02_config,
                        self.a03_execute_sql,
                        self.a04_test_method]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_strings, action_funcs)


    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_summary(self):
        print("... displaying high level summary ...")


    def a02_config(self):
        print("... adjust settings here ...")


    def a03_execute_sql(self):
        with sqlite3.connect(DATABASE_DIRECTORY) as conn:
            cur = conn.cursor()
            conn.set_trace_callback(print)
            cur.execute(
                "update `category` set `parent_id` = '1000000050' where `category_id` = '1000000026'"
            )
            conn.set_trace_callback(None)
        return cur.fetchall()


    def a04_test_method(self):
        print("... executing test method ...")
        account_names = dbh.account.get_account_names()
        print(account_names)


# TODO: finish this function to reboot the program (for instance if code source changed)
    def a05_reboot(self):
        pass


4