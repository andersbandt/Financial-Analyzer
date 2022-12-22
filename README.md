# Financial-Analyzer
Analyzes spending, budget, and investment data in a GUI

**TO ANYONE JOINING RECENTLY**
Discord server [here](https://discord.gg/qRKYKUzy)

## Requirements
- Python3
- python3-virtualenv
- python3-pip

## Local Setup
1. Clone the repo:
    ```bash
    git clone https://github.com/andersbandt/Financial-Analyzer
    cd Financial-Analyzer
    ```
2. Initialize and activate a virtual environment:
    ```bash
    virtualenv env
    source env/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

4. Run the application:
    ```bash
    python3 main.py
    ```

## Tab Organization

### Investment Tab

- Need section for displaying every active investment with ticker, latest price, and value
- Provide a broad overview of portfolio allocation across accounts
- Have section for displaying total per account_id (of type III only)


## SQL Organization

Database organization is split among many tables.

### Table: account
-	account_id
-	name 32 character max
  -	**type** *INT* Integer representing account type (checking, credit, investment, etc.)
        - 0 = checking 
        - 1 = saving 
        - 2 = credit 
        - 3 = investment 
        - 4 = other

### Table: category
- category_id
- name (32 character max)
- parent ID of the ‘parent’ category. For example (GYM is a child category of HEALTH).

### Table: keywords
- **category_id**
- **keyword** *VARCHAR(32)* 32 letter keyword for certain category_id.

### Table: ledger
- **key** *INT* Primary key for SQL data in ledger. Properties is that it is 
auto incrementing.
- **trans_date** *DATE* SQL object of type DATE used for representing the transaction date
- **account_id** *INT(10) 10 digits representing account ID that the transaction is from
- **category_id** *INT(10)* 10 digits representing category that the transaction belongs to
- **amount** *NUMERIC(10,2)* Float value with max 2 decimal points for transaction value.
- **trans_description** *VARCHAR(200)* String for representing a description of the transaction.
- **trans_note** *VARCHAR(200)* String for any transaction notes (optional)
- **date_added** *DATETIME* Date + time that the transaction was added to the ledger

### Table: budget
- **category_id**: *INT(10)* 10 digits representing category that the transaction belongs to
- **lim**: *NUMERIC(10,2)* representing the limit on that category
- **cd**: *INT* representing if we count downwards or not when analyzing this budget. Used for 
savings/spendings budget goals. A cd of **0** means we are counting downwards (spending goal).
A cd of **1** means that we are counting upwards (savings goal).
- not sure exactly what else I need here? But might be nice to add some columns.

### Table: balances
-	**key** *INT* Primary key
-	**account_id** What account the balance pertains to
  -	**amount** *NUMERIC(10, 2)* representing account balance
    **bal_date** *DATE* data type representing account balance record date

### Table: investment
- **key** *INT* Primary key
- **trans_date** *DATE* SQL object of type DATE used for representing the transaction date
- **account_id** *INT(10)* account_id
- **ticker** *VARCHAR(8)* String for standard ticker of asset
- **shares** *NUMERIC(10,2)* Number of shares transacted
- **value** *NUMERIC(10,2)* Dollar amount of transaction
- **calc_type** *INT*
  - 0 for manual entry
  - 1 for automatic calculation (either based on pulling historical price data, etc.)
- **inv_type** *INT* "type" of investment. For example...
  - 1 for pure stock
  - 2 for mutual fund
  - 3 for bonds
  - 4 for crypto
  - 5 for cash


## Description of MAIN functions

### graphing_analyzer.py (analyzing)

THIS FUNCTION SETS WHICH ACCOUNT_ID CORRESPONDS TO WHAT ACCOUNT TYPE

## Description of HELPER functions

### analyzer_helper.py (analyzing)
Very general helper module for more of the mathematical analysis side of the analyzing

### graphing_helper.py (analyzing)
Very good module for turning Transaction and Category data into formats needed for graphing. 

### gui_helper.py (Finance_GUI)
Assists in a lot of GUI functions (alerts, errors, printing to prompts). Also contains some methods
for drawing content on the screen

### db_helper.py (db)
Module for performing financial database operations. Things such as adding, editing, and recalling data
from all the various parts of the financial app.

### load_helper.py (tools)
Modules for assisting with loading data from raw source material. Raw source material mainly is .csv
files, so functions assist with manipulating data in many different formats. Also handles checking
status of loaded in data.

### date_helper.py (tools)
This helper contains a lot of critical functions working with dates.

### scraping_helper.py (Scraping)
NEEDS TO BE DEPRECATED OFFICIALLY

## Class Descriptions

### Transaction
A class representing a single transaction. Has some properties like categorization
and retrieving information. Variables are pretty much the SQL columns.

### Ledger
This is the basic class for a list of Transaction objects

### Statement - inherits from Ledger
This is for loading in new data from an account statement. I have basically created
a class that inherits from Statement for each account with only the *load_statement_data*
method overriden depending on the format that the account data comes in

## Budget Analysis Workings

Budget analysis will be based on the Category objects created in the Tree.

There will have to be some error handling to determine if the sum of all children is greater than the 
cap of the parent budget.

IDEA: For software implementation, might want to make Budget a subcategory of Category?

## Investments

### Investment Type
There is a number that sets what type of investment each is. This should be set in a document.


## Raw financial data structure

On my computer I have a folder where I store all the statements for each account. Each month
I go to the accounts and download a file representing all the account information for each
month. Typically this is .csv format. The file structure for the data looks like:


- 2020
  - Monthly Statements
    - 01-January
    - 02-February
    - ...
    - 12-December
- 2021
  - Monthly Statements
    - 01-January
    - ...
    - 12-December

And so on for as many years as you want to create.

## How to load in data in ap

1.	Select year and month, then select file from dropdown of that menu
2.	Then select account from another dropdown
3.	Hit a button to load in the file
4.	A statement object will be created on the GUI depending on what type of account it is
5.	All transaction data will be loaded


## Things to Work On
Features, ideas, and things that need improvement.

### Code Cleanup

- One thing to add to make the code prettier is to create a general class for data adding. Notice that I use a very similar 
layout for adding a Category, keyword, budget category. I could create a general class for that. 
- Another thing could be creating an InvestmentTransaction object based on the Transaction 
- Make a general tab object that all tabs inherit from. Could add some
properties like hide tab or some shit
- Have GUI elements like dropdowns auto regenerate when an event like a new account
gets added

## Resources

### General
- [Financial Budget Analysis with Python - thecleverprogrammer.com](https://thecleverprogrammer.com/2021/04/05/financial-budget-analysis-with-python/)

### Graphing
- [Funnel charts with plotly](https://plotly.com/python/funnel-charts/)

### Other Budget Trackers
- [Ledger CLI](https://www.ledger-cli.org/)
- [hledger](https://hledger.org/)
- 



