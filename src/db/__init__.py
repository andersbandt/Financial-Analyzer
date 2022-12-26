import sqlite3 
DATABASE_DIRECTORY = '../src/db/financials.db'

class TableStatements:
    """
    A class for holding the SQL statements.
    """
    ledger =     '''CREATE TABLE ledger
                    (key         INTEGER  PRIMARY KEY AUTOINCREMENT,
                    trans_date   DATE,
                    account_id   INT(10),
                    category_id  INT(10),
                    amount       NUMERIC(10,2),
                    description  VARCHAR(300),
                    note         VARCHAR(300),
                    date_added   DATETIME);''' 
    account =    '''CREATE TABLE account
                    (account_id   INT(10) PRIMARY KEY,
                    name          VARCHAR(32),
                    type          INT(10));'''
    category =   '''CREATE TABLE category
                    (category_id    INT(10) PRIMARY KEY,
                    parent          INT(10),
                    name            VARCHAR(32));'''
    #TODO: decide if it should be 'keywords' or 'keyword'
    keyword =    '''CREATE TABLE keywords 
                    (id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id    INT(10),
                    keyword        VARCHAR(32));'''
    #TODO: Decide if this table is going to be used. It was in the comments section below so I added it here.
    # budget =     '''CREATE TABLE budget
    #                 (category_id    INT PRIMARY KEY ,
    #                 lim           NUMERIC(10,2) ,
    #                 cd              INT(10));'''

def all_tables_init(statements: list, database_directory: str) -> bool:
    """
    Create all the tables. It uses a list instead 
    of importing the TableStatements class for 
    dependency injection reasons.
    """
    with sqlite3.connect(database_directory) as conn:
        cursor = conn.cursor()
        for statement in statements:
            cursor.execute(statement)

# alter ledger table structure
# try:
# 	conn.execute("ALTER TABLE ledger ADD COLUMN note VARCHAR(300);")
# 	conn.execute("ALTER TABLE ledger ADD COLUMN date_added DATETIME;")
# except sqlite3.Error as er:
# 	print("\nUh oh, something went wrong adding columns to table ledger")
# 	print(er)
# else:
# 	print("Table ledger edited successfully")

# copy over ledger data
# try:
# 	conn.execute("INSERT INTO ledger_new SELECT * FROM ledger;")
# except sqlite3.Error as er:
# 	print("\nUh oh, something went wrong copying table ledger into ledger_new")
# 	print(er)
# else:
# 	print("Table 'ledger' copied succesfully")



# try:
# 	answer = input("Would you actually like to drop the investment table?: y or n")
# 	if answer == "y":
# 		conn.execute("DROP TABLE investment")
# 		print("Ok dropped table investment")
# 	else:
# 		print("Ok, not dropping table")
# 	conn.execute('''CREATE TABLE investment
# 		(key            INTEGER PRIMARY KEY AUTOINCREMENT,
# 		trans_date      DATE,
# 		account_id      INT(10),
# 		ticker          VARCHAR(32),
# 		shares          NUMERIC(10,2),
# 		value           NUMERIC(10,2),
# 		calc_type       INT,
# 		inv_type        INT);''')
# except sqlite3.Error as er:
# 	print("\nUh oh, something went wrong with table creation for: investment")
# 	print(er)
# else:
# 	print("Table 'investment' created successfully")




