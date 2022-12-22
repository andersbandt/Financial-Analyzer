import sqlite3 
DATABASE_DIRECTORY = 'src/db/financials.db'

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
    Create all the tables. If any of the _table_init() functions
    return False, print the error message that sqlite3 threw.

    It uses a list instead of importing the TableStatements class
    for reusability reasons.
    
    It also maintains the ability to get which statement threw an
    exception. 
    """
    with sqlite3.connect(database_directory) as conn:
        # If we didn't want to capture which statements threw exceptions,
        # we could use a for loop to iterate through the statements list.
        # for statement in statements:
        #     create_table(conn, statement)
        
        ledger = create_table(conn, statements[0])
        account = create_table(conn, statements[1])
        category = create_table(conn, statements[2])
        keyword = create_table(conn, statements[3])

    
    results = [ledger, account, category, keyword] 
        
    if all(results) == True:
        print("All tables initialized successfully.")
        return True
    else: 
        for result in results:
            print(result) 
        return False 

def create_table(conn: sqlite3, statement: str) -> bool:
    try:
        conn.execute(statement)
        return True
    except sqlite3.Error as error:
        return str(error) 

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




