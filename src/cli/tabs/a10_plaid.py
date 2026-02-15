"""
@file a10_plaid.py
@brief sub menu for Plaid API integration - link accounts and sync transactions

"""

# import needed packages
import time
from datetime import date, timedelta, datetime
from prettytable import PrettyTable

# import user defined CLI modules
import cli.cli_helper as clih
import cli.cli_printer as clip
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import Plaid integration modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from plaid_integration import plaid_config
from plaid_integration import plaid_service
from plaid_integration import plaid_adapter
import db.helpers as dbh
from db.helpers import plaid as plaid_db
from tools import load_helper as loadh

# import logger
from loguru import logger


class TabPlaid(SubMenu):
    def __init__(self, title, basefilepath):
        self.basefilepath = basefilepath
        self.plaid_client = None

        # initialize information about sub menu options
        action_arr = [
            Action("Configure Plaid credentials", self.a01_configure),
            Action("Link bank account", self.a02_link_account),
            Action("Sync transactions", self.a03_sync_transactions),
            Action("View linked accounts", self.a04_view_accounts),
            Action("Unlink account", self.a05_unlink_account),
        ]

        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

    ##############################################################################
    ####      HELPER FUNCTIONS           #########################################
    ##############################################################################

    def _initialize_plaid_client(self):
        """Initialize Plaid client from config file"""
        if self.plaid_client is not None:
            return True

        credentials = plaid_config.load_credentials()
        if credentials is None:
            print("\n❌ No Plaid credentials found!")
            print(f"   Config file location: {plaid_config.get_config_path()}")
            print("   Please run 'Configure Plaid credentials' first.\n")
            return False

        self.plaid_client = plaid_service.initialize_client(
            credentials['client_id'],
            credentials['secret'],
            credentials['environment']
        )

        if self.plaid_client is None:
            print("\n❌ Failed to initialize Plaid client!")
            return False

        return True

    ##############################################################################
    ####      ACTION FUNCTIONS           #########################################
    ##############################################################################

    def a01_configure(self):
        """Configure Plaid API credentials"""
        print("\n" + "="*80)
        print("CONFIGURE PLAID CREDENTIALS")
        print("="*80)
        print("\nYou'll need a Plaid account to use this feature.")
        print("Sign up at: https://dashboard.plaid.com/signup")
        print("\nYou can find your credentials in the Plaid Dashboard:")
        print("  1. Go to Team Settings -> Keys")
        print("  2. Copy your client_id and secret")
        print("\n" + "-"*80)

        # Check if config already exists
        if plaid_config.config_exists():
            print(f"\n⚠️  Config file already exists at: {plaid_config.get_config_path()}")
            if not clih.promptYesNo("Do you want to overwrite existing credentials?"):
                print("Cancelled.")
                return False

        # Get credentials from user
        print("\nEnter your Plaid credentials:")
        client_id = clih.spinput("Client ID", "text")
        if not client_id:
            return False

        secret = clih.spinput("Secret", "text")
        if not secret:
            return False

        # Get environment
        print("\nSelect environment:")
        print("  1. Sandbox (for testing, uses fake data)")
        print("  2. Development (real data, limited to 100 items)")
        print("  3. Production (requires approval from Plaid)")

        env_choice = clih.spinput("Environment (1-3)", "int")
        if not env_choice or env_choice < 1 or env_choice > 3:
            print("Invalid choice.")
            return False

        env_map = {1: 'sandbox', 2: 'development', 3: 'production'}
        environment = env_map[env_choice]

        # Save credentials
        success = plaid_config.save_credentials(client_id, secret, environment)

        if success:
            print(f"\n✅ Credentials saved successfully!")
            print(f"   Environment: {environment}")
            print(f"   Config file: {plaid_config.get_config_path()}")

            # Test connection
            print("\nTesting connection...")
            self.plaid_client = None  # Reset client
            if self._initialize_plaid_client():
                print("✅ Connection successful!")
            else:
                print("❌ Connection failed. Please check your credentials.")
        else:
            print("\n❌ Failed to save credentials.")

        return True

    def a02_link_account(self):
        """Link a bank account via Plaid Link"""
        print("\n" + "="*80)
        print("LINK BANK ACCOUNT")
        print("="*80)

        # Initialize Plaid client
        if not self._initialize_plaid_client():
            return False

        # Create Link token
        print("\nCreating Link token...")
        user_id = f"user_{int(time.time())}"  # Simple user ID based on timestamp
        link_token = self.plaid_client.create_link_token(user_id)

        if link_token is None:
            print("❌ Failed to create Link token.")
            return False

        print("\n" + "-"*80)
        print("PLAID LINK FLOW")
        print("-"*80)
        print("\nTo link your account, you need to complete the Plaid Link flow.")
        print("This is typically done in a web browser, but for CLI usage,")
        print("we'll use a simplified flow.\n")

        print("Link Token:", link_token)
        print("\nIn a production app, you would:")
        print("  1. Open Plaid Link in a browser with this token")
        print("  2. Select your bank and authenticate")
        print("  3. Return with a public_token")
        print("\nFor development/testing, you can use Plaid's sandbox.")
        print("-"*80)

        # Get public token from user
        public_token = clih.spinput("\nEnter the public_token from Plaid Link (or 'q' to cancel)", "text")
        if not public_token:
            print("Cancelled.")
            return False

        # Exchange public token for access token
        print("\nExchanging public token for access token...")
        result = self.plaid_client.exchange_public_token(public_token)

        if result is None:
            print("❌ Failed to exchange token.")
            return False

        access_token, item_id = result
        print(f"✅ Successfully obtained access token!")
        print(f"   Item ID: {item_id}")

        # Get accounts from Plaid
        print("\nRetrieving account information...")
        accounts = self.plaid_client.get_accounts(access_token)

        if accounts is None or len(accounts) == 0:
            print("❌ No accounts found.")
            return False

        # Display accounts
        print(f"\n✅ Found {len(accounts)} account(s):")
        print("-"*80)
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account['name']} ({account['official_name']})")
            print(f"   Type: {account['type']} - {account['subtype']}")
            print(f"   Balance: ${account['balances']['current']}")
            print(f"   Mask: ***{account['mask']}")
            print()

        # Prompt user to select which Plaid account to link
        if len(accounts) == 1:
            selected_idx = 0
        else:
            choice = clih.spinput(f"Select account to link (1-{len(accounts)})", "int")
            if not choice or choice < 1 or choice > len(accounts):
                print("Invalid choice.")
                return False
            selected_idx = choice - 1

        selected_account = accounts[selected_idx]
        plaid_account_id = selected_account['account_id']
        plaid_institution_id = item_id

        # Map to existing account in our database
        print("\n" + "-"*80)
        print("MAP TO EXISTING ACCOUNT")
        print("-"*80)
        print("Select which account in your database this maps to:\n")

        our_account_id = clih.account_prompt_all("Select account")
        if not our_account_id:
            print("Cancelled.")
            return False

        # Store access token in database
        print("\nStoring access token...")
        success = plaid_db.insert_access_token(
            our_account_id,
            access_token,
            plaid_account_id,
            plaid_institution_id
        )

        if success:
            print(f"\n✅ Account linked successfully!")
            print(f"   Plaid Account: {selected_account['name']}")
            print(f"   Our Account: {dbh.account.get_account_name_from_id(our_account_id)}")
            print(f"   Account ID: {our_account_id}")
            print("\nYou can now sync transactions using 'Sync transactions'.")
        else:
            print("\n❌ Failed to store access token.")

        return True

    def a03_sync_transactions(self):
        """Sync transactions from Plaid"""
        print("\n" + "="*80)
        print("SYNC TRANSACTIONS")
        print("="*80)

        # Initialize Plaid client
        if not self._initialize_plaid_client():
            return False

        # Get linked accounts
        linked_accounts = plaid_db.get_plaid_linked_accounts()

        if not linked_accounts:
            print("\n❌ No linked accounts found.")
            print("   Please link an account first using 'Link bank account'.")
            return False

        # Display linked accounts
        print(f"\nFound {len(linked_accounts)} linked account(s):")
        print("-"*80)
        for i, acc in enumerate(linked_accounts, 1):
            last_synced = acc['last_synced'] or "Never"
            print(f"{i}. {acc['name']} ({acc['institution_name']})")
            print(f"   Last synced: {last_synced}")
            print(f"   Transactions: {acc['transaction_count']}")
            print()

        # Select account
        if len(linked_accounts) == 1:
            selected_idx = 0
        else:
            choice = clih.spinput(f"Select account to sync (1-{len(linked_accounts)})", "int")
            if not choice or choice < 1 or choice > len(linked_accounts):
                print("Invalid choice.")
                return False
            selected_idx = choice - 1

        selected = linked_accounts[selected_idx]
        account_id = selected['account_id']

        # Get access token
        access_token = plaid_db.get_access_token(account_id)
        if not access_token:
            print("❌ Failed to retrieve access token.")
            return False

        # Get date range
        print("\n" + "-"*80)
        print("SELECT DATE RANGE")
        print("-"*80)
        print("Enter the date range for transactions to sync.")
        print("(Leave blank for last 30 days)")

        # Default: last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        use_default = clih.promptYesNo(f"Use default range ({start_date} to {end_date})?")
        if not use_default:
            year = clih.spinput("Start year (YYYY)", "int")
            month = clih.spinput("Start month (1-12)", "int")
            day = clih.spinput("Start day (1-31)", "int")
            if not all([year, month, day]):
                print("Cancelled.")
                return False
            start_date = date(year, month, day)

            year = clih.spinput("End year (YYYY)", "int")
            month = clih.spinput("End month (1-12)", "int")
            day = clih.spinput("End day (1-31)", "int")
            if not all([year, month, day]):
                print("Cancelled.")
                return False
            end_date = date(year, month, day)

        # Fetch transactions from Plaid
        print(f"\nFetching transactions from {start_date} to {end_date}...")
        plaid_response = self.plaid_client.get_transactions(access_token, start_date, end_date)

        if plaid_response is None:
            print("❌ Failed to fetch transactions.")
            # Update sync state with error
            plaid_db.update_sync_state(account_id, datetime.now(), error_msg="Failed to fetch transactions")
            return False

        transaction_count = len(plaid_response['transactions'])
        print(f"✅ Retrieved {transaction_count} transaction(s)")

        if transaction_count == 0:
            print("No transactions found in this date range.")
            return False

        # Convert to Statement
        print("\nConverting to Statement object...")
        # Use the middle month/year from the range for Statement
        mid_date = start_date + (end_date - start_date) / 2
        statement = plaid_adapter.plaid_response_to_statement(
            plaid_response,
            account_id,
            mid_date.year,
            mid_date.month
        )

        if statement is None:
            print("❌ Failed to convert transactions.")
            return False

        # Check for duplicates
        print("\nChecking for duplicates...")
        new_transactions = []
        duplicate_count = 0

        for trans in statement.ledger:
            if plaid_db.check_transaction_by_plaid_id(trans.plaid_transaction_id):
                duplicate_count += 1
            else:
                new_transactions.append(trans)

        print(f"   New transactions: {len(new_transactions)}")
        print(f"   Duplicates (skipped): {duplicate_count}")

        if len(new_transactions) == 0:
            print("\nNo new transactions to import.")
            plaid_db.update_sync_state(account_id, datetime.now())
            return True

        # Update statement ledger with only new transactions
        statement.ledger = new_transactions

        # Display preview
        print("\n" + "="*80)
        print("TRANSACTION PREVIEW")
        print("="*80)
        statement.print_statement()

        # Proceed with categorization
        print("\n" + "-"*80)
        if not clih.promptYesNo("Proceed with categorization?"):
            print("Cancelled.")
            return False

        # Categorize automatically
        print("\nCategorizing transactions automatically...")
        statement.categorizeLedgerAutomatic()

        # Check for uncategorized
        uncategorized = [t for t in statement.ledger if t.category_id == 0]
        if uncategorized:
            print(f"\n⚠️  {len(uncategorized)} transaction(s) remain uncategorized.")
            if clih.promptYesNo("Manually categorize remaining transactions?"):
                statement.categorize_manual()

        # Save to database
        print("\n" + "-"*80)
        if not clih.promptYesNo("Save transactions to database?"):
            print("Cancelled.")
            return False

        print("\nSaving transactions...")
        statement.save_statement()

        # Update sync state
        plaid_db.update_sync_state(account_id, datetime.now())

        print(f"\n✅ Successfully synced {len(new_transactions)} transaction(s)!")
        return True

    def a04_view_accounts(self):
        """View all Plaid-linked accounts"""
        print("\n" + "="*80)
        print("PLAID-LINKED ACCOUNTS")
        print("="*80)

        linked_accounts = plaid_db.get_plaid_linked_accounts()

        if not linked_accounts:
            print("\n❌ No linked accounts found.")
            print("   Use 'Link bank account' to connect an account.")
            return False

        # Create table
        table = PrettyTable()
        table.field_names = ["ID", "Name", "Institution", "Last Synced", "Transactions", "Status"]

        for acc in linked_accounts:
            last_synced = acc['last_synced'] or "Never"
            if acc['last_synced']:
                # Format datetime
                try:
                    dt = datetime.fromisoformat(acc['last_synced'])
                    last_synced = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass

            # Check for errors
            status = "✅ OK"
            if acc['sync_state'] and acc['sync_state']['last_error_message']:
                status = f"❌ Error: {acc['sync_state']['last_error_message'][:30]}"

            table.add_row([
                acc['account_id'],
                acc['name'],
                acc['institution_name'],
                last_synced,
                acc['transaction_count'],
                status
            ])

        print("\n" + str(table))
        print(f"\nTotal: {len(linked_accounts)} linked account(s)")
        return True

    def a05_unlink_account(self):
        """Unlink a Plaid account"""
        print("\n" + "="*80)
        print("UNLINK ACCOUNT")
        print("="*80)

        # Initialize Plaid client
        if not self._initialize_plaid_client():
            return False

        # Get linked accounts
        linked_accounts = plaid_db.get_plaid_linked_accounts()

        if not linked_accounts:
            print("\n❌ No linked accounts found.")
            return False

        # Display accounts
        print(f"\nLinked accounts:")
        print("-"*80)
        for i, acc in enumerate(linked_accounts, 1):
            print(f"{i}. {acc['name']} ({acc['institution_name']})")
            print(f"   Transactions: {acc['transaction_count']}")
            print()

        # Select account
        choice = clih.spinput(f"Select account to unlink (1-{len(linked_accounts)})", "int")
        if not choice or choice < 1 or choice > len(linked_accounts):
            print("Invalid choice.")
            return False

        selected = linked_accounts[choice - 1]
        account_id = selected['account_id']

        # Confirm
        print("\n⚠️  WARNING: This will unlink the account from Plaid.")
        print("   Historical transactions will remain in your database.")
        print("   You will need to re-link if you want to sync new transactions.")

        if not clih.promptYesNo(f"Are you sure you want to unlink '{selected['name']}'?"):
            print("Cancelled.")
            return False

        # Get access token and revoke
        access_token = plaid_db.get_access_token(account_id)
        if access_token:
            print("\nRevoking Plaid access...")
            self.plaid_client.revoke_access(access_token)

        # Remove from database
        print("Removing from database...")
        success = plaid_db.revoke_access_token(account_id)

        if success:
            print(f"\n✅ Account unlinked successfully!")
        else:
            print("\n❌ Failed to unlink account.")

        return True
