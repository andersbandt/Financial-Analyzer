"""
@file a04_load_data.py
@brief sub menu for loading in raw financial data and storing in database

"""

# import needed packages
import csv
import time

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import needed GUI modules
import tkinter as tk
from tkinter import filedialog

# import user defined helper modules
from statement_types.Transaction import Transaction
from categories import categories_helper as cath
from account import account_helper as acch
from tools import load_helper as loadh
import db.helpers as dbh
from tools import date_helper as dateh
from db import app_settings

# import logger
from loguru import logger


class TabLoadData(SubMenu):
    def __init__(self, title, basefilepath):
        self.statement = None
        self.basefilepath = basefilepath  # had to add this in, at some point maybe delete?
        self.updated = False

        # initialize information about sub menu options
        action_arr = [
            Action("Load data", self.a01_load_data),
            Action("Load ALL data", self.a02_load_all_data),
            Action("Load single file", self.a03_load_single_file),
            Action("Add manual transaction", self.a04_add_manual_transaction),
            Action("Perform data integrity audit", self.a05_check_status),
            Action("Manage recurring transactions", self.a11_manage_recurring_transactions),
            Action("Apply recurring transactions (paycheck deductions)", self.a12_apply_recurring_transactions),
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_load_data(self):
        print("... loading in financial data for certain year/month ...")

        # get month / year combination to examine in
        year_month = clih.prompt_year_month()
        if year_month is False:
            return False
        [year, month] = year_month

        # create list of Statement objects for each file for the particular month/year combination
        statement_list = loadh.get_month_year_statement_list(
            self.basefilepath,
            year,
            month,
            printmode=True) # NOTE: printmode controls the printing of each individual statement file
        logger.debug(f"Statement list --> {statement_list}")
        logger.debug(f"Statement list has length {len(statement_list)}")

        # join statement list into one "master" statement
        self.statement = loadh.join_statement(statement_list)

        logger.debug(f"Final monthly statement has {len(self.statement.transactions)} transactions")

        # apply any active recurring transactions (paycheck deductions, HSA/401k contributions,
        # etc.) for this month -- see "Manage recurring transactions" / "Apply recurring
        # transactions" for the standalone version of this (paychecks are usually biweekly,
        # not monthly, so this hook is a convenience, not the only way to apply them).
        if clih.promptYesNo("Do you want to apply recurring transactions (paycheck deductions) for this month?"):
            default_date = dateh.month_year_to_date_range(year, month)[1]
            self.apply_recurring_transactions(default_date, target_statement=self.statement)

        self.statement.print_statement()
        self.update_listing()
        return True

    def a02_load_all_data(self):
        print("... loading in ALL financial data")
        statement_list = []
        year_range = dateh.get_valid_years()

        for year in year_range:
            for month in range(1, 12 + 1):
                tmp_list = loadh.get_month_year_statement_list(self.basefilepath, year, month, printmode=True)
                statement_list.extend(tmp_list)

        print("\t... finished creating all Statement objects in range")
        print("\nCreating master Ledger object")
        self.statement = loadh.join_statement(statement_list)

        print("\t... done creating Ledger object.\n Updating listings and exiting.")
        self.update_listing()

    def a03_load_single_file(self):
        # Create a Tkinter root window and hide it
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Open a file dialog and prompt the user to select a file
        file_path = filedialog.askopenfilename(title="Select a file")
        if not file_path:
            return False

        self.statement = loadh.create_statement("dummy-year", "dummy-month", file_path, account_id_prompt=True)
        # TODO: probably standardize the below code and make another function in load_helper.py?
        try:
            self.statement.load_statement_data()
        except Exception as e:
            print("Something went wrong loading statement from filepath!!!\n\terror is: ", e)
            raise e

        self.statement.print_statement()
        self.update_listing()
        return True

    def a04_add_manual_transaction(self):
        print("... attempting to manually load in a transaction. Kinda scary. Don't mess up.")

        # get account information
        account_id = clih.account_prompt_all("What is the account for this one-time transaction?")
        time.sleep(0.2)
        if account_id is False or account_id is None:
            return False

        # get description
        description = clih.spinput("What is the transaction description?: ", "text")
        time.sleep(0.2)

        # get amount
        amount = clih.spinput("What is the transaction amount?: ", "float")
        time.sleep(0.2)
        if amount is False or amount is None:
            return False

        # get category information
        category_id = clih.category_prompt_all("What is the category to search for?: ", False)
        time.sleep(0.2)
        if category_id is False or category_id is None:
            return False

        # prompt user for date
        trans_date = clih.get_date_input("\nand what date is this balance record for?: ")
        time.sleep(0.2)
        if trans_date is False or trans_date is None:
            return False

        # create transaction
        transaction = Transaction(trans_date, account_id, category_id, amount, description, note="MANUALLY ADDED")

        # INSERT TRANSACTION
        success = dbh.ledger.insert_transaction(transaction)
        return success

    def a05_check_status(self):
        print("... checking data status ...")

        # get user input on which method to use
        print("Two method for data integrity checking")
        print("METHOD 1: checks for presence of files on the system matching to certain accounts")
        print("METHOD 2: actually pulls data from files and sees if it exists in the database")
        method_num = clih.spinput("What type of data integrity method to use?", inp_type="int")

        # set up information on which account(s) we are interested in
        acc_id_arr = []
        acc_types = [acch.types.SAVING.value,
                     acch.types.CHECKING.value,
                     acch.types.CREDIT_CARD.value]
        for at in acc_types:
            acc_id_arr.extend(acch.get_account_id_by_type(at))

        if method_num == 1:
            self.check_data_integrity_01(acc_id_arr)
        elif method_num == 2:
            self.check_data_integrity_02(acc_id_arr)

    ##############################################################################
    ####      RECURRING TRANSACTIONS (paycheck deductions, etc.)     #############
    ##############################################################################

    # apply_recurring_transactions: applies every ACTIVE recurring_transaction preset for `date`.
    #   Each preset writes its main (category) transaction, plus -- if add_complementary is set --
    #   a same-account, opposite-sign transaction under complementary_category_id, so deductions
    #   that never show up on a bank statement (health insurance, HSA/401k, taxes, ...) still show
    #   up in category/income reporting without changing the account's recorded balance.
    #   @param date               date to post the transactions on (e.g. the actual pay date)
    #   @param target_statement   if given (called mid statement-load), append the new
    #                             Transactions to it so they get saved along with the rest of
    #                             that month's statement, matching the old hardcoded behavior.
    #                             If None (standalone use), insert into the DB immediately.
    def apply_recurring_transactions(self, date, target_statement=None):
        presets = dbh.recurring_transaction.get_all_recurring_transactions(active_only=True)
        if not presets:
            print("No active recurring transactions configured. Use 'Manage recurring transactions' to add some.")
            return []

        target_month = date[:7]  # "YYYY-MM" -- string-prefix compare, dates are stored as ISO text
        created = []
        applied_count = 0
        for row in presets:
            (rid, name, account_id, category_id, default_amount, description,
             add_complementary, complementary_category_id, active, note) = row

            # double-apply guard: warn if this preset already posted a transaction this
            # calendar month (e.g. you ran Load Data twice for the same month). Per-preset,
            # so you can skip the ones already done and still apply anything new.
            applied_this_month = sorted({
                d for d in dbh.recurring_transaction.get_applied_dates(rid) if d[:7] == target_month
            })
            if applied_this_month:
                print(f"\n{name}: already applied on {', '.join(applied_this_month)} this month.")
                if not clih.promptYesNo(f"  Apply '{name}' again for {target_month} anyway?"):
                    print(f"  Skipped '{name}'.")
                    continue

            print(f"\n{name}  (default {default_amount:+.2f}  |  "
                  f"{acch.account_id_to_name(account_id)} / {cath.category_id_to_name(category_id)})")
            amount_inp = input(f"  Amount for this occurrence [enter to accept {default_amount:+.2f}]: ").strip()
            if amount_inp == "":
                amount = default_amount
            else:
                try:
                    amount = float(amount_inp.replace(",", ""))
                except ValueError:
                    print("  Invalid number, using default.")
                    amount = default_amount

            txns = [Transaction(date, account_id, category_id, amount, description,
                                 note=f"recurring_transaction id={rid}")]

            if add_complementary:
                comp_category_id = complementary_category_id
                if comp_category_id is None:
                    comp_category_id = cath.category_name_to_id("INCOME")
                txns.append(Transaction(date, account_id, comp_category_id, -1 * amount,
                                         f"{description} (complementary)",
                                         note=f"recurring_transaction id={rid} (complementary)"))

            for t in txns:
                if target_statement is not None:
                    target_statement.add_transaction(t)
                else:
                    dbh.transactions.insert_transaction(t)
                created.append(t)
            applied_count += 1

        dest = "current statement (save it to persist)" if target_statement is not None else "database"
        print(f"\nApplied {applied_count}/{len(presets)} recurring transaction preset(s) "
              f"({len(presets) - applied_count} skipped), creating {len(created)} row(s) in the {dest}.")
        return created

    def a11_manage_recurring_transactions(self):
        while True:
            presets = dbh.recurring_transaction.get_all_recurring_transactions(active_only=False)
            print("\n--- Recurring transactions (paycheck deductions, etc.) ---")
            if not presets:
                print("  (none configured yet)")
            for row in presets:
                (rid, name, account_id, category_id, amount, description,
                 add_complementary, complementary_category_id, active, note) = row
                status = "ACTIVE" if active else "inactive"
                comp = (f" + complementary -> {cath.category_id_to_name(complementary_category_id)}"
                        if add_complementary and complementary_category_id is not None else "")
                print(f"  [{rid}] {name:<30} {amount:>+9.2f}  "
                      f"{acch.account_id_to_name(account_id)} / {cath.category_id_to_name(category_id)}"
                      f"{comp}  ({status})")

            action = clih.prompt_num_options(
                "Action?", ["Add new", "Edit existing", "Toggle active/inactive", "Delete", "Done"])
            if action is False or action == 5:
                return True
            elif action == 1:
                self._add_recurring_transaction_prompt()
            elif not presets:
                print("Nothing to edit/toggle/delete yet -- add one first.")
            elif action == 2:
                self._edit_recurring_transaction_prompt(presets)
            elif action == 3:
                self._toggle_recurring_transaction_prompt(presets)
            elif action == 4:
                self._delete_recurring_transaction_prompt(presets)

    def a12_apply_recurring_transactions(self):
        print("... applying active recurring transactions (e.g. paycheck deductions) ...")
        pay_date = clih.get_date_input(
            "What date should these recurring transactions be posted on? (e.g. your actual pay date)")
        if pay_date is False or pay_date is None:
            return False
        return self.apply_recurring_transactions(pay_date, target_statement=None)

    def _select_recurring_transaction(self, presets, prompt_str):
        labels = [f"[{row[0]}] {row[1]}" for row in presets]
        idx = clih.prompt_num_options(prompt_str, labels)
        if idx is False:
            return None
        return presets[idx - 1]

    def _add_recurring_transaction_prompt(self):
        print("\n--- Add recurring transaction ---")
        name = clih.spinput("Short name (e.g. 'HSA Contribution')", "text")
        if name is False:
            return False

        account_id = clih.account_prompt_all(
            "Which account does this post to? (usually wherever your paycheck lands)")
        if account_id in (False, None):
            return False

        category_id = clih.category_prompt_all("Category for this deduction/line item?", False)
        if category_id in (False, None):
            return False

        amount = clih.spinput(
            "Default amount per occurrence (negative = money out, e.g. -225.00 for a deduction)", "float")
        if amount is False:
            return False

        description = clih.spinput("Transaction description (shown in the ledger)", "text")
        if description is False or description == "":
            description = name

        add_complementary = clih.promptYesNo(
            "Add an offsetting complementary transaction too? Recommended for paycheck deductions -- "
            "your account only ever sees the NET deposit, so this 'grosses up' income/spending reports "
            "without changing the account balance."
        )
        complementary_category_id = None
        if add_complementary:
            complementary_category_id = clih.category_prompt_all(
                "Category for the complementary (offsetting) leg? (usually INCOME)", False)
            if complementary_category_id in (False, None):
                return False

        note = clih.spinput("Optional note (enter to skip)", "text")
        if note is False or note == "":
            note = None

        rid = dbh.recurring_transaction.insert_recurring_transaction(
            name, account_id, category_id, amount, description,
            add_complementary=add_complementary,
            complementary_category_id=complementary_category_id,
            note=note,
        )
        print(f"Created recurring transaction #{rid}.")
        return True

    def _edit_recurring_transaction_prompt(self, presets):
        row = self._select_recurring_transaction(presets, "Edit which recurring transaction?")
        if row is None:
            return False
        (rid, name, account_id, category_id, amount, description,
         add_complementary, complementary_category_id, active, note) = row

        field = clih.prompt_num_options(
            f"Editing '{name}' -- which field?",
            ["Name", "Amount", "Description", "Category", "Account", "Complementary category", "Note", "Cancel"])
        if field is False or field == 8:
            return False

        if field == 1:
            new_val = clih.spinput("New name", "text")
            if new_val is not False:
                dbh.recurring_transaction.update_recurring_transaction(rid, name=new_val)
        elif field == 2:
            new_val = clih.spinput(f"New amount (was {amount:+.2f})", "float")
            if new_val is not False:
                dbh.recurring_transaction.update_recurring_transaction(rid, amount=new_val)
        elif field == 3:
            new_val = clih.spinput("New description", "text")
            if new_val is not False:
                dbh.recurring_transaction.update_recurring_transaction(rid, description=new_val)
        elif field == 4:
            new_val = clih.category_prompt_all("New category?", False)
            if new_val not in (False, None):
                dbh.recurring_transaction.update_recurring_transaction(rid, category_id=new_val)
        elif field == 5:
            new_val = clih.account_prompt_all("New account?")
            if new_val not in (False, None):
                dbh.recurring_transaction.update_recurring_transaction(rid, account_id=new_val)
        elif field == 6:
            new_val = clih.category_prompt_all("New complementary category?", False)
            if new_val not in (False, None):
                dbh.recurring_transaction.update_recurring_transaction(rid, complementary_category_id=new_val)
        elif field == 7:
            new_val = clih.spinput("New note", "text")
            if new_val is not False:
                dbh.recurring_transaction.update_recurring_transaction(rid, note=new_val)

        print("Updated.")
        return True

    def _toggle_recurring_transaction_prompt(self, presets):
        row = self._select_recurring_transaction(presets, "Toggle active status of which recurring transaction?")
        if row is None:
            return False
        rid, active = row[0], row[8]
        dbh.recurring_transaction.set_recurring_transaction_active(rid, not bool(active))
        print(f"Recurring transaction #{rid} is now {'ACTIVE' if not active else 'inactive'}.")
        return True

    def _delete_recurring_transaction_prompt(self, presets):
        row = self._select_recurring_transaction(presets, "Delete which recurring transaction?")
        if row is None:
            return False
        rid, name = row[0], row[1]
        if clih.promptYesNo(f"Really delete recurring transaction '{name}' (#{rid})? "
                             f"This does not affect transactions already applied from it."):
            dbh.recurring_transaction.delete_recurring_transaction(rid)
            print("Deleted.")
            return True
        return False

    ########              ##########################              ########
    #######  BELOW FUNCTIONS AVAILABLE AFTER STATEMENT IS LOADED IN ######
    ######################                          ######################

    # a03_categorize_statement: helps user categorize currently loaded statement data
    def a06_categorize_statement(self):
        print("\n\na03: Automatically categorizing Statement")
        categories = cath.load_categories()

        self.statement.categorizeLedgerAutomatic(categories)

        auto_categorized = [t for t in self.statement.transactions if t.note and "keyword=" in t.note]
        if auto_categorized:
            clip.print_variable_table(
                ["DATE", "AMOUNT", "DESC", "CATEGORY", "NOTE"],
                [[t.date, t.value, t.description, cath.category_id_to_name(t.category_id), t.note]
                 for t in auto_categorized],
                title=f"Auto-categorized ({len(auto_categorized)} transactions)",
            )

        self.statement.print_statement(sort_by_category=True)

        # ML categorization runs automatically (no per-load prompt) when enabled via
        # Main Dash > System configuration. Toggle with app_settings.set_ml_categorization_on_load().
        if app_settings.get_ml_categorization_on_load():
            self.statement.categorize_ml()

            ml_categorized = [t for t in self.statement.transactions if t.note and "ml_classified" in t.note]
            if ml_categorized:
                clip.print_variable_table(
                    ["DATE", "AMOUNT", "DESC", "CATEGORY", "NOTE"],
                    [[t.date, t.value, t.description, cath.category_id_to_name(t.category_id), t.note]
                     for t in ml_categorized],
                    title=f"ML-categorized ({len(ml_categorized)} transactions)",
                )

            self.statement.print_statement(sort_by_category=True)

        res = clih.promptYesNo("Do you want to attempt manual categorization of remaining transactions?")
        if res:
            _, manually_categorized = self.statement.categorize_manual()
            if manually_categorized:
                print(f"\n--- {len(manually_categorized)} transaction(s) manually categorized ---")
                headers = ["DATE", "AMOUNT", "DESC", "CATEGORY", "NOTE"]
                values = [
                    [t.date, t.value, t.description,
                     cath.category_id_to_name(t.category_id), t.note]
                    for t in manually_categorized
                ]
                clip.print_variable_table(headers, values)
        else:
            print("Ok, leaving statement with just automatic categorization applied")

        # give the user a quick chance to fix any miscategorized transaction (by its "#" row
        # number) right here, instead of having to hunt for it in the menu afterward.
        if clih.promptYesNo("Do you want to edit any transaction's category (by #) before moving on?"):
            self.statement.edit_transaction_category_cli()

    # a05_save_statement_csv: saves the currently loaded statement to a .csv file
    def a07_save_statement_csv(self):
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
    def a08_print_ledger(self):
        print(" ... printing current Ledger object")
        self.statement.sort_date_desc()
        self.statement.print_statement()

    # a07_sort_ledger: sorts the ledger by some metric
    def a09_sort_ledger(self):
        print(" ... sorting Ledger object")
        strings_arr = ["amount up", "amount down", "date up", "date down", "categorization method"]
        method = clih.inp_auto("Enter sorting method", strings_arr, echo=True)

        if method == strings_arr[0]:
            self.statement.sort_trans_asc()
        elif method == strings_arr[1]:
            self.statement.sort_trans_desc()
        elif method == strings_arr[2]:
            self.statement.sort_date_asc()
        elif method == strings_arr[3]:
            self.statement.sort_date_desc()
        elif method == strings_arr[4]:
            self.statement.sort_categorization_method()
        else:
            return False

        # re-print the statement
        self.statement.print_statement()
        return True

    # a13_edit_transaction_category: lets the user fix any transaction's category by its "#"
    #   row number (printed alongside every statement table), rather than only being able to
    #   re-run full (auto/ml/manual) categorization. Available any time after a statement is
    #   loaded -- not just right after "Categorize statement" -- so it also covers cases like
    #   spotting a miscategorized transaction while sorting/printing later.
    def a13_edit_transaction_category(self):
        print("\n... editing transaction categor(ies) by row number ...")
        return self.statement.edit_transaction_category_cli()

    def a10_save_statement_db(self):
        print("... saving statement to .db file ...")
        res = clih.promptYesNo("Are you sure you want to save the statement?")
        if res:
            status = self.statement.save_statement()
            return status
        else:
            return False

    ##############################################################################
    ####      OTHER HELPER FUNCTIONS           ###################################
    ##############################################################################

    # NOTE: this method only checks file presence on disk, not what is in the database (that is method 2's job).
    #   If a filename changed over time (e.g. CreditCard3.csv -> CreditCard4.csv), this will show false gaps.
    #   Fix is a data fix: add BOTH filename patterns to the file_mapping table pointing to the same account_id.
    #   No code change needed — match_file_to_account() already does pattern matching against that table.
    def check_data_integrity_01(self, acc_id_arr):
        acc_data_status = []
        bad_months = {acc_id: [] for acc_id in acc_id_arr}  # To track BAD months per account

        # Loop through month/year combos
        for year in dateh.get_valid_years():
            for month in range(1, 12 + 1):
                # Get list of files in that directory
                month_year_dir = loadh.get_year_month_files(self.basefilepath, year, month)
                tmp_month_status = [f"{year}-{month:02d}"]  # zero-padded so it sorts/reads correctly

                for acc_id in acc_id_arr:
                    def find_account_match(aid):
                        for file in month_year_dir:
                            tmp_account_id = loadh.match_file_to_account(file)
                            if tmp_account_id == aid:
                                return True
                        return False

                    # Append if match was found or not
                    if find_account_match(acc_id):
                        tmp_month_status.append("1")
                    else:
                        tmp_month_status.append("0")

                acc_data_status.append(tmp_month_status)

        # Process the data to find "BAD" patterns
        for acc_idx, acc_id in enumerate(acc_id_arr, start=1):
            account_status = [row[acc_idx] for row in acc_data_status]  # Extract data for the account
            for i in range(1, len(account_status)):
                # Check for a 1 followed by a 0
                if account_status[i - 1] == "1" and account_status[i] == "0":
                    bad_months[acc_id].append(acc_data_status[i][0])  # Log the bad month (year-month)

        # keep the full 0/1 grid available at DEBUG level, but it's unreadable as a printed
        # table once there are more than a handful of accounts (columns wrap into garbage) --
        # the per-account summary below is the actual actionable output.
        field_names = ["Month"] + [dbh.account.get_account_name_from_id(acc_id) for acc_id in acc_id_arr]
        logger.debug(field_names)
        logger.debug(acc_data_status)

        # summary table: one row per account, worst offenders (most gaps) first
        summary_rows = [
            [acch.account_id_to_name(acc_id), len(months), ", ".join(months) if months else "-"]
            for acc_id, months in bad_months.items()
        ]
        summary_rows.sort(key=lambda r: -r[1])
        clip.print_variable_table(
            ["Account", "# Gaps", "Gap months (file present, then missing)"],
            summary_rows,
            min_width=12, max_width=60, max_width_column="Gap months (file present, then missing)",
            title="Data integrity check -- Method 1 (file presence on disk)",
        )

        n_clean = sum(1 for r in summary_rows if r[1] == 0)
        logger.info(f"{n_clean}/{len(acc_id_arr)} account(s) have no detected gaps.")

        return True

    # NOTE: mismatches are expected and have two root causes — this method is unreliable as-is:
    #   1. DUPLICATE DETECTION: re-loading a file counts all transactions in it, but previously-flagged
    #      duplicates were never saved to DB, so file count > DB count for already-loaded months. This is
    #      correct behavior, not a bug, but it makes the comparison noisy.
    #   2. DATE BOUNDARIES: get_transaction_count() uses an exclusive upper bound (first day of next month)
    #      while statement files may contain transactions at month edges. Minor but adds more false mismatches.
    #   REAL FIX: the file_history table (in schema) was intended to track loaded files and would make this
    #   method reliable — but it was never implemented (no DB helper, never written to). To fix properly:
    #   write to file_history in save_statement(), add a db helper to query it, then method 2 can simply
    #   check file_history instead of re-parsing every file.
    def check_data_integrity_02(self, acc_id_arr):
        """
        Checks data integrity by comparing the total count of transactions in files
        with the total count of transactions in the database for each month/year/account_id combo.
        """
        # Initialize results dictionary
        integrity_results = {}
        mismatch_rows = []
        parse_errors = []  # (year, month, filepath, error_str) -- see get_month_year_statement_list

        # Loop through valid years
        for year in dateh.get_valid_years():
            # Loop through months in the year
            for month in range(1, 13):
                # Get list of statement objects for the month/year. raise_on_error=False so a
                # single old/malformed file (e.g. a stray '*' in an amount column) doesn't abort
                # the whole scan -- it's recorded in parse_errors and reported below instead.
                statements = loadh.get_month_year_statement_list(
                    self.basefilepath, year, month, printmode=False,
                    raise_on_error=False, error_log=parse_errors)

                # loop through statements and compare to database
                for statement in statements:
                    # get amount of transactions in relevant, just-loaded statement
                    statement_transaction_count = len(statement.transactions)

                    # Fetch transaction count from the database
                    db_transaction_count = dbh.transactions.get_transaction_count(statement.account_id, year, month)

                    # Store results for comparison
                    integrity_results[(year, month, statement.account_id)] = {
                        "file_transactions": statement_transaction_count,
                        "db_transactions": db_transaction_count,
                        "matches": statement_transaction_count == db_transaction_count,
                    }

                    if statement_transaction_count != db_transaction_count:
                        mismatch_rows.append([
                            f"{year}-{month:02d}",
                            acch.account_id_to_name(statement.account_id),
                            statement_transaction_count,
                            db_transaction_count,
                        ])

        # Report mismatches
        if mismatch_rows:
            clip.print_variable_table(
                ["Month", "Account", "File count", "DB count"],
                mismatch_rows,
                title=f"Data integrity check -- Method 2 ({len(mismatch_rows)} count mismatch(es))",
            )
        else:
            logger.info("Method 2: no file/DB transaction count mismatches found.")

        # Report files that couldn't even be parsed, separately -- these are worth fixing
        # regardless of what the count comparison says (the file just never got counted at all)
        if parse_errors:
            clip.print_variable_table(
                ["Month", "Filepath", "Error"],
                [[f"{y}-{m:02d}", f, e] for (y, m, f, e) in parse_errors],
                min_width=12, max_width=60, max_width_column="Error",
                title=f"Method 2: {len(parse_errors)} file(s) failed to parse (not counted above)",
            )

        # Return results for further processing or debugging
        return True

    def update_listing(self):
        if self.updated == False:
            # append new actions to menu now that statement is loaded in
            new_actions = [
                Action("Categorize statement", self.a06_categorize_statement),
                Action("Save to .csv", self.a07_save_statement_csv),
                Action("Print new Ledger", self.a08_print_ledger),
                Action("Sort ledger", self.a09_sort_ledger),
                Action("Edit transaction category", self.a13_edit_transaction_category),
                Action("Save to database", self.a10_save_statement_db),
            ]
            self.action_arr.extend(new_actions)
            self.updated = True
            return True
        else:
            return False

