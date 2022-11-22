# Financial-Analyzer
Analyzes spending, budget, and investment data in a GUI



## SQL Organization

Database Organization
Table: account
-	account_id
-	name
o	32 character max
-	type 
- Integer representing account type (checking, credit, investment, etc.)
- 0 = checking 
- 1 = saving 
- 2 = credit 
- 3 = investment 
- 4 = other

Table: category
-	category_id
  -	name (32 character max)
-	parent
o	ID of the ‘parent’ category. For example (GYM is a child category of HEALTH).

Table: keywords
-	category_id
-	keyword
o	32 letter keyword

Table: ledger
-	key
o	auto increment primary key
-	trans_date
o	DATE SQL object
-	account_id
o	10 digits representing account ID that the transaction is from
-	category_id
o	10 digits representing category that the transaction belongs to
-	amount
o	NUMERIC(10,2)
-	trans_description
o	VARCHAR item with 200 character max. Represents a description of the transaction.

Table: budget
-	category_id
o	10 digits representing category that the transaction belongs to
-	limit
o	NUMERIC(10,2) representing the limit on that category
-	Countdown
o	Boolean representing if we count downwards or not when analyzing this budget

Table: balances
-	key
o	Integer
o	Primary key
-	account_id
o	What account the balance pertains to
-	amount
o	NUMERIC(10, 2) representing account balance
-	Bal_date
o	DATE data type representing account balance record date




 



## Description of MAIN functions

### graphing_analyyzer.py (analyzing)

THIS FUNCTION SETS WHICH ACCOUNT_ID CORRESPONDS TO WHAT ACCOUNT TYPE

## Description of HELPER functions

### analyzer_helper.py (analyzing)

### graphing_helper.py (analyzing)

### gui_helper.py (Finance_GUI)
assists in a lot of GUI functions (alerts, errors, printing to prompts)


### investment_helper.py (analyzing)


### db_helper.py (db)



### load_helper.py (tools)
This helper contains a lot of critical functions working with DATES

### scraping_helper.py (Scraping)



