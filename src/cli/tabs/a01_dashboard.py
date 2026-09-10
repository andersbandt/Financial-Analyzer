

# import needed packages
import sqlite3
import os
import sys


# import user defined modules
from db import DATABASE_DIRECTORY
from db import helpers as dbh
from db import app_settings
from cli.cli_class import SubMenu
from cli.cli_class import Action
import cli.cli_helper as clih


class TabMainDashboard(SubMenu):
    def __init__(self, title, basefilepath):
        # initialize information about sub menu options
        action_arr = [Action("High level summary", self.a01_summary),
                      Action("System configuration", self.a02_config),
                      Action("Execute RAW SQL statement", self.a03_execute_sql),
                      Action("TEST METHOD", self.a04_test_method),
                      Action("Reboot program", self.a05_reboot)
                      ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_summary(self):
        print("... displaying high level summary ...")

    def a02_config(self):
        while True:
            ml = app_settings.get_ml_categorization_on_load()
            guard = app_settings.get_db_guard_on_startup()

            print("\n--- System configuration ---")
            print(f"  1. ML categorization on statement load : {'ENABLED' if ml else 'DISABLED'}")
            print(f"  2. Database sync guard on startup      : {'ENABLED' if guard else 'DISABLED'}")
            print("  0. Back")

            choice = clih.spinput("Toggle which setting? (0 to go back)", inp_type="int")
            if choice is False or choice == 0:
                return

            if choice == 1:
                print("\nWhen enabled, the Load Data tab automatically runs the ML classifier on any "
                      "transactions keyword matching missed, before falling back to manual categorization.")
                if clih.promptYesNo(f"Do you want to {'DISABLE' if ml else 'ENABLE'} ML categorization on load?"):
                    app_settings.set_ml_categorization_on_load(not ml)
                    print(f"  -> ML categorization on load is now {'ENABLED' if not ml else 'DISABLED'}.")
                else:
                    print("  Setting unchanged.")

            elif choice == 2:
                print("\nThe DB sync guard runs multi-machine safety checks at startup: OneDrive "
                      "conflict-copy\ndetection, a SQLite integrity check, a local (non-synced) backup, "
                      "and a lock file that\nwarns if the app looks open on your other machine.")
                if guard:
                    print("\n  WARNING: disabling this removes ALL of those protections.")
                    if not clih.promptYesNo("  Really DISABLE the DB sync guard?"):
                        print("  Setting unchanged.")
                        continue
                    app_settings.set_db_guard_on_startup(False)
                    print("  -> DB sync guard is now DISABLED.")
                else:
                    app_settings.set_db_guard_on_startup(True)
                    print("  -> DB sync guard is now ENABLED.")

            else:
                print("  Invalid choice.")

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

    # MAIN ISSUE RIGHT NOW. It reboots and prints out but still thinks I've exited and am in the bash shell.
    # .... honestly I have some doubts this is even possible .....
    def a05_reboot(self):
        os.execv(sys.executable, ['python'] + sys.argv)

