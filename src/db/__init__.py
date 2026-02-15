
# import needed modules
import sqlite3

# setup database master file
DATABASE_DIRECTORY = "C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/financials.db" # tag:hardcode


"""
A class for holding the SQL statements.
"""
# below is list of all the various tables
# support for 9,999,999,999 billion dollars with SQL data type of INT(10)
class TableStatements:

# NOTE: was having weird thing where "transaction" was throwing an error but "transactions" was working
    transactions = """CREATE TABLE transactions
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    date                    DATE,
                    account_id              INT(10) REFERENCES account(account_id),
                    category_id             INT(10) REFERENCES category(category_id),
                    amount                  NUMERIC(10,2),
                    description             VARCHAR(300),
                    name                    VARCHAR(300),
                    note                    VARCHAR(300),
                    date_added              DATETIME);"""
    account = """CREATE TABLE account
                    (account_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    name                    VARCHAR(50),
                    institution_name        VARCHAR(50),
                    type                    INT(10),
                    balance                 NUMERIC(10,2), 
                    algorithm               INT(10),
                    balance_updated_date    DATE,
                    retirement              BOOLEAN,
                    savings_goal            INT(10));"""
    category = """CREATE TABLE category
                    (category_id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id               INT(10) REFERENCES category(category_id),
                    name                    VARCHAR(32));"""
    keyword = """CREATE TABLE keywords
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id             INT(10) REFERENCES category(category_id),
                    keyword                    VARCHAR(32));"""
    budget = """CREATE TABLE budget
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id             INT(10) REFERENCES category(id),
                    amount                  INT(10),
                    applies_to_children     BOOLEAN);"""
    balance = """CREATE TABLE balance
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              INT(10) REFERENCES account(id),
                    amount                  NUMERIC(10,2),
                    bal_date                DATE);"""
    investment = """CREATE TABLE investment
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    date                    DATE,
                    account_id              FOREIGN KEY INT(10) REFERENCES account(id),
                    category_id             INT(10) REFERENCES category(id),
                    ticker                  VARCHAR,
                    shares                  NUMERIC(10,2),
                    trans_type              VARCHAR(30),
                    value                   NUMERIC(10,2),
                    description             VARCHAR(300),
                    note                    VARCHAR(300),
                    date_added              DATETIME);"""
    file_mapping = """CREATE TABLE file_mapping
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              FOREIGN KEY INT(10) REFERENCES account(id),
                    file_search_str         VARCHAR(300));"""
    file_history = """CREATE TABLE file_history
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              FOREIGN KEY INT(10) REFERENCES account(id),
                    file_name               VARCHAR(300));"""
    goals = """CREATE TABLE goals
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              FOREIGN KEY INT(10) REFERENCES account(id),
                    amount                  NUMERIC(10,2),
                    date                    DATE)"""
    ticker_metadata = """CREATE TABLE ticker_metadata
                    (ticker                 VARCHAR(10) PRIMARY KEY,
                    asset_type              VARCHAR(50),
                    name                    VARCHAR(100),
                    last_updated            DATETIME)"""
    plaid_sync_state = """CREATE TABLE plaid_sync_state
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              INT(10) REFERENCES account(account_id),
                    last_successful_sync    DATETIME,
                    last_attempted_sync     DATETIME,
                    last_error_message      VARCHAR(500),
                    sync_count              INT DEFAULT 0,
                    cursor                  VARCHAR(1000),
                    is_syncing              BOOLEAN DEFAULT 0);"""
    plaid_credentials = """CREATE TABLE plaid_credentials
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id_encrypted     BLOB,
                    secret_key_encrypted    BLOB,
                    environment             VARCHAR(20),
                    created_at              DATETIME,
                    is_active               BOOLEAN DEFAULT 1);"""


"""
Create all the tables. It uses a list instead
of importing the TableStatements class for
dependency injection reasons.
"""
def all_tables_init(statements: list, database_directory: str) -> bool:
    try:
        with sqlite3.connect(database_directory) as conn:
            cursor = conn.cursor()
            for statement in statements:
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    pass
            conn.set_trace_callback(None)
    except sqlite3.OperationalError as e:
        print(f"\n{e}")
        print(f"Yikes, couldn't open your database file")
        print(f"\n\n##########################################################")
        print(f"\n\tYour path is currently \n\t{database_directory}. ")
        print(f"\n##########################################################")
        print(f"\nPlease review filepath and make any needed adjustments in src/db/__init__.py. Around line 6 ish\n\n")
        return False
    print("\n\n")
    return True


def migrate_plaid_schema(database_directory: str):
    """One-time migration to add Plaid support to existing databases"""
    migration_statements = [
        "ALTER TABLE account ADD COLUMN plaid_account_id VARCHAR(100)",
        "ALTER TABLE account ADD COLUMN plaid_institution_id VARCHAR(100)",
        "ALTER TABLE account ADD COLUMN access_token_encrypted BLOB",
        "ALTER TABLE account ADD COLUMN access_token_synced DATETIME",
        "ALTER TABLE account ADD COLUMN is_plaid_linked BOOLEAN DEFAULT 0",

        "ALTER TABLE transactions ADD COLUMN plaid_transaction_id VARCHAR(100)",
        "ALTER TABLE transactions ADD COLUMN plaid_account_id VARCHAR(100)",
        "ALTER TABLE transactions ADD COLUMN transaction_source VARCHAR(20) DEFAULT 'MANUAL'",
        "ALTER TABLE transactions ADD COLUMN plaid_synced_at DATETIME",

        "CREATE UNIQUE INDEX IF NOT EXISTS idx_plaid_transaction ON transactions(plaid_transaction_id) WHERE plaid_transaction_id IS NOT NULL",
        "CREATE INDEX IF NOT EXISTS idx_plaid_account ON account(plaid_account_id)",
    ]

    with sqlite3.connect(database_directory) as conn:
        cursor = conn.cursor()
        for statement in migration_statements:
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as e:
                # Column/index already exists, skip
                pass


def populate_tables(database_directory: str):
    account_statement = """
        insert into `account` (`account_id`, `name`, `type`) values (2000000001, 'U.S. Bank', 1);
        insert into `account` (`account_id`, `name`, `type`) values (2000000002, 'WELLS CHECKING', 2);
    """

    keyword_statement = """
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000001, 1, 'TRADER JOE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 2, 'SPOTIFY');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000001, 3, 'MCDONALDS');
    """

    categories_statement = """
        insert into `category` (`category_id`, `name`, `parent_id`) values (0, 'NA', 0);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000001, 'FOOD AND DRINK', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000002, 'LIVING', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000003, 'MEDIA', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000004, 'LESIURE', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000005, 'SHOPPING', 1);
    """

    # alter_statement = """
    #     ALTER TABLE account ADD COLUMN retirement BOOLEAN;
    # """

    statements = [account_statement, categories_statement, keyword_statement]
    with sqlite3.connect(database_directory) as conn:
        # conn.set_trace_callback(print)
        cursor = conn.cursor()
        for statement in statements:
            try:
                cursor.executescript(statement)
            except sqlite3.IntegrityError as e:
                pass
                # print(e)
        conn.set_trace_callback(None)
