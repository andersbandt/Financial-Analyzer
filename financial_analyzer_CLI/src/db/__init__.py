
# import needed modules
import sqlite3

# setup database master file
DATABASE_DIRECTORY = "C:/Users/ander/OneDrive/Code/python/financial_analyzer_CLI/src/db/financials.db" # tag:hardcode


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
                    balance_updated_date    DATE
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
                    amount                  NUMERIC(10,2));"""
    investment = """CREATE TABLE investment
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    date                    DATE,
                    account_id              INT(10) REFERENCES account(id),
                    category_id             INT(10) REFERENCES category(id),
                    ticker                  VARCHAR,
                    shares                  NUMERIC(10,2),
                    trans_type              VARCHAR(30),
                    value                   NUMERIC(10,2),
                    description             VARCHAR(300),
                    note                    VARCHAR(300),
                    date_added              DATETIME);"""
    file_history = """CREATE TABLE file_history
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              INT(10) REFERENCES account(id),
                    file_name               VARCHAR(300));"""
    goals = """CREATE TABLE goals
                    (id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id              INT(10) REFERENCES account(id),
                    amount                  NUMERIC(10,2),
                    date                    DATE)"""

"""
Create all the tables. It uses a list instead
of importing the TableStatements class for
dependency injection reasons.
"""
def all_tables_init(statements: list, database_directory: str) -> bool:
    print("Initializing all tables in database .db file!!! Exciting!!!")
    with sqlite3.connect(database_directory) as conn:
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        for statement in statements:
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as e:
                print(e)
        conn.set_trace_callback(None)
    print("\n\n")


def populate_tables(database_directory: str):
    account_statement = """
        insert into `account` (`account_id`, `name`, `type`) values (2000000001, 'MARCUS', 1);
        insert into `account` (`account_id`, `name`, `type`) values (2000000002, 'WELLS CHECKING', 2);
        insert into `account` (`account_id`, `name`, `type`) values (2000000003, 'WELLS SAVING', 1);
        insert into `account` (`account_id`, `name`, `type`) values (2000000004, 'WELLS CREDIT', 3);
        insert into `account` (`account_id`, `name`, `type`) values (2000000005, 'VANGUARD BROKERAGE', 4);
        insert into `account` (`account_id`, `name`, `type`) values (2000000006, 'VANGUARD ROTH', 4);
        insert into `account` (`account_id`, `name`, `type`) values (2000000007, 'VENMO', 2);
        insert into `account` (`account_id`, `name`, `type`) values (2000000008, 'ROBINHOOD', 4);
        insert into `account` (`account_id`, `name`, `type`) values (2000000009, 'APPLE CARD', 3);
        insert into `account` (`account_id`, `name`, `type`) values (2000000010, 'FIDELITY', 4);
        insert into `account` (`account_id`, `name`, `type`) values (2000000011, 'HSA', 4);
        insert into `account` (`account_id`, `name`, `type`) values (2000000012, 'CHASE CREDIT', 3);
    """

    keyword_statement = """
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000006, 1, 'TRADER JOE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 2, 'SCIENTIFIC AMERICAN');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 6, 'MCDONALDS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 7, 'CHIPOTLE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 8, 'MACTAGGARTS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000015, 9, 'TRANSFER');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000021, 10, 'UBER');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 11, 'MONDAY''S');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 12, 'CHASERS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000024, 13, 'INTEREST');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 14, 'KOLLEGE KLUB');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 15, 'TACO BELL');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000022, 16, 'NGANLAM');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 18, 'HENDERSON TAP HOUSE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000018, 19, 'NTTA');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 20, 'THE STANDARD POUR');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 21, 'SKELLIG');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000037, 23, 'DIR DEP');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 24, 'DALL12500');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000036, 25, 'LEMONADE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 26, 'Patreon');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000006, 27, 'CENTRAL MARKET');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 28, 'CANES');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000005, 30, 'eBay');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000016, 31, 'EPAY');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 32, 'TEXAS INSTRUMENTS DALLAS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000031, 33, 'AMERICAN AIR');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000026, 34, 'EXXON');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 35, 'HULU');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000032, 36, 'STARBUCKS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000031, 37, 'DFW AIRPORT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1111111111, 38, 'LA FITNESS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000006, 39, 'WAL-MART');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000022, 40, 'MAA WEB');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 41, 'TRAIL ICE HOUSE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000012, 42, 'MAKERSPACE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000034, 43, 'MR. WINSTON');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000005, 44, 'AMZN');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000023, 45, 'Jessica Herman');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000025, 46, 'energy');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000016, 47, 'PAYMENT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 48, 'FOX AND HOUND');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 49, 'Chelseas Corner');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000005, 51, 'HOME DEPOT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000012, 52, 'OBSIDIAN');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000022, 53, 'WEB PMTS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000026, 55, 'SHELL OIL');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000007, 56, 'NORDSTROM');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000017, 57, 'CAVA');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000046, 58, 'LA FIT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 59, 'LEANN CHIN');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 60, 'McDonalds');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000016, 61, 'PAYMENT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000023, 62, 'GE3UNITED');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000023, 63, 'DIRECT DEP');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 64, 'SOUNDCLOUD');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000006, 65, 'WOODMANS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000001, 66, 'PIZZA');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 67, 'QDOBA');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 68, 'MCDONALD''S');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000005, 69, 'ALIEXPRESS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000001, 70, 'JIMMY JOHNS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 71, 'JIMMY JOHNS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000045, 72, 'MOBILE DEPOSIT');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000046, 73, 'GNC');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000018, 74, 'PARKMOBILE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000003, 75, 'SPOTIFY');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000009, 76, 'LIQOUR');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 77, 'LEANN CHIN');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000018, 78, 'AIRLINE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000026, 83, 'RACETRAC');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000012, 84, 'ACE HILLDALE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000044, 85, 'TRANSACTION FEE');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000042, 87, 'IN N OUT BURGER');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000047, 88, 'DIGI KEY');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000049, 89, 'GREAT CLIPS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000010, 90, 'HAPPIEST HOUR');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000049, 91, 'HIMS');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000009, 92, 'LIQUOR');
    insert into `keywords` (`category_id`, `id`, `keyword`) values (1000000044, 93, 'FEE');
    """

    categories_statement = """
        insert into `category` (`category_id`, `name`, `parent_id`) values (0, 'NA', 0);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000001, 'FOOD AND DRINK', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000002, 'LIVING', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000003, 'MEDIA', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000004, 'LESIURE', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000005, 'SHOPPING', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000006, 'GROCERY', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000007, 'CLOTHING', 1000000005);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000008, 'GYM', 1000000046);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000009, 'LIQOUR STORE', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000010, 'BARS', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000011, 'EYECARE', 1000000046);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000012, 'HOBBIES', 1000000004);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000013, 'DENTIST', 1000000046);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000014, 'INTERNAL', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000015, 'TRANSFER', 1000000014);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000016, 'PAYMENT', 1000000014);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000017, 'EATING OUT', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000018, 'TRANSPORTATION', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000019, 'BALANCE', 1000000014);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000020, 'MUSIC', 1000000003);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000021, 'RIDESHARE', 1000000018);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000022, 'RENT', 1000000036);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000023, 'INCOME', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000024, 'INTEREST', 1000000023);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000025, 'ENERGY', 1000000036);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000026, 'GAS', 1000000018);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000027, 'INVESTMENT', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000028, 'SHARES', 1000000027);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000029, 'DIVIDENDS', 1000000027);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000030, 'VALUE', 1000000027);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000031, 'TRAVEL', 1000000004);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000032, 'CAFFIENE', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000033, 'MAKING', 1000000012);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000034, 'HYGIENE', 1000000046);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000035, 'RACES', 1000000012);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000036, 'HOUSING', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000037, 'PAYCHECK', 1000000023);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000038, 'THC', 0);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000039, 'CAR', 0);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000040, 'RESTAURANT', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000041, 'GIVING', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000042, 'FAST FOOD', 1000000001);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000043, 'MISC FINANCE', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000044, 'FEE', 1000000043);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000045, 'GIFT', 1000000043);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000046, 'HEALTH', 1);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000047, 'ELECTRONICS', 1000000033);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000048, 'CRYTPO', 1000000043);
        insert into `category` (`category_id`, `name`, `parent_id`) values (1000000049, 'COSMETICS', 1000000034);
    """

    statements = [account_statement, categories_statement, keyword_statement]
    with sqlite3.connect(database_directory) as conn:
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        for statement in statements:
            try:
                cursor.executescript(statement)
            except sqlite3.OperationalError as e:
                print(e)
        conn.set_trace_callback(None)
