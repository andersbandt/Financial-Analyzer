import sqlite3

conn = sqlite3.connect('financials.db')
print("Opened database successfully")



try:
	conn.execute("DROP TABLE ledger")
except sqlite3Error as er:
	print("\nUh oh, something went wrong with dropping table ledger")
	print(er)
else:
	print("Dropped table ledger")



try:
	conn.execute('''CREATE TABLE ledger
		(key         INTEGER  PRIMARY KEY AUTOINCREMENT,
		trans_date   DATE,
		account_id   INT(10),
		category_id  INT(10),
		amount       NUMERIC(10,2),
		description  VARCHAR(300));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: ledger")
	print(er)
else:
	print("Table 'ledger' created successfuly")



try:
	conn.execute('''CREATE TABLE account
		(account_id   INT(10) PRIMARY KEY,
		name          VARCHAR(32));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: account")
	print(er)
else:
	print("Table 'account' created successfuly")


try:
	conn.execute('''CREATE TABLE category
		(category_id    INT(10) PRIMARY KEY,
		parent          INT(10),
		name            VARCHAR(32));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: category")
	print(er)
else:
	print("Table 'category' created successfuly")


try:
	conn.execute('''CREATE TABLE keywords
		(id            INTEGER PRIMARY KEY AUTOINCREMENT,
		category_id    INT(10),
		keyword        VARCHAR(32));''')
except sqlite3.Error as er:
	print("\nUh oh, something went wrong with table creation for: keyword")
	print(er)
else:
	print("Table 'keyword' created successfuly")




conn.close()
