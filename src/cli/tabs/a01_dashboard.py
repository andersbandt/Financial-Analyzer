# import needed packages
import sqlite3

# import user defined modules
from db import DATABASE_DIRECTORY
from db import helpers as dbh
from cli.cli_class import SubMenu
from cli.cli_class import Action


class TabMainDashboard(SubMenu):
    def __init__(self, title, basefilepath):
        # initialize information about sub menu options
        action_arr = [Action("High level summary", self.a01_summary),
                      Action("System configuration", self.a02_config),
                      Action("Execute RAW SQL statement", self.a03_execute_sql),
                      Action("TEST METHOD", self.a04_test_method)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

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
