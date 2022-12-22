import sqlite3

conn = sqlite3.connect('financials.db')
print("Opened database successfully")


# create ledger table
try:
	conn.execute('''CREATE TABLE ledger
		(key         INTEGER  PRIMARY KEY AUTOINCREMENT,
		trans_date   DATE,
		account_id   INT(10),
		category_id  INT(10),
		amount       NUMERIC(10,2),
		description  VARCHAR(300),
		note         VARCHAR(300),
		date_added   DATETIME);''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: ledger")
	print(er)
else:
	print("Table 'ledger' created successfully")


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


# create account table
try:
	conn.execute('''CREATE TABLE account
		(account_id   INT(10) PRIMARY KEY,
		name          VARCHAR(32),
		type          INT(10));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: account")
	print(er)
else:
	print("Table 'account' created successfully")


# create category table
try:
	conn.execute('''CREATE TABLE category
		(category_id    INT(10) PRIMARY KEY,
		parent          INT(10),
		name            VARCHAR(32));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: category")
	print(er)
else:
	print("Table 'category' created successfully")


# create keyword table
try:
	conn.execute('''CREATE TABLE keywords
		(id            INTEGER PRIMARY KEY AUTOINCREMENT,
		category_id    INT(10),
		keyword        VARCHAR(32));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: keyword")
	print(er)
else:
	print("Table 'keyword' created successfully")


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


# try:
# 	conn.execute('''CREATE TABLE balances
# 		(key            INTEGER PRIMARY KEY AUTOINCREMENT,
# 		account_id      INT(10),
# 		amount          NUMERIC(10,2),
# 		bal_date        DATE);''')
# except sqlite3.Error as er:
# 	print("\nUh oh, something went wrong with table creation for: balances")
# 	print(er)
# else:
# 	print("Table 'balances' created successfully")


# try:
# 	conn.execute('''CREATE TABLE budget(
# 		category_id    INT PRIMARY KEY ,
# 		lim           NUMERIC(10,2) ,
# 		cd              INT(10));''')
# # (category_id   INT(10) PRIMARY KEY
# # limit          NUMERIC(10,2),
# # cd             INT(10);''')
# except sqlite3.Error as er:
# 	print("\nUh oh, something went wrong with table creation for: budget")
# 	print(er)
# else:
# 	print("Table 'budget' created successfully")


conn.close()



