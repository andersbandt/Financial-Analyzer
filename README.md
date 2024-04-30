<<<<<<< HEAD
# Financial-Analyzer
Analyzes spending, budget, and investment data in a GUI

**TO ANYONE JOINING RECENTLY**
Discord server [here](https://discord.gg/qRKYKUzy)

## Setup Information

### Requirements
- Python3
- python3-virtualenv
- python3-pip

### Local Setup
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

4. To run the Tkinter based version of the application:
    ```bash
    cd /backend
    python3 main.py
    ```
    
### Financial Data File Structure

On my computer I have a folder where I store all the statements for each account. You can
download a sample file folder structure with `sample_financials_folder_structure.zip`. Each month
I go to the accounts and download a file representing all the account information for each
month. Typically, this is .csv format. The file structure for the data looks like:

For example - all under "C:\Users\bob\Documents\Financials\"

- Monthly Statement\2020\
    - 01-January\
    - 02-February\
    - ...
    - 12-December
- Monthly Statements\2021\
    - 01-January\
    - ...
    - 12-December\

And so on for as many years as you want to create.


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


## How to load in data in application

1.	Select year and month, then select file from dropdown of that menu
2.	Then select account from another dropdown
3.	Hit a button to load in the file
4.	A statement object will be created on the GUI depending on what type of account it is
5.	All transaction data will be loaded


## Resources

### General
- [Financial Budget Analysis with Python - thecleverprogrammer.com](https://thecleverprogrammer.com/2021/04/05/financial-budget-analysis-with-python/)

### Graphing
- [Funnel charts with plotly](https://plotly.com/python/funnel-charts/)

### Other Budget Trackers
- [Ledger CLI](https://www.ledger-cli.org/)
- [hledger](https://hledger.org/)
- 



=======
# Financial-Analyzer
This project is meant for analysis of personal financial data in a CLI (command line interface) application.

This project used to leverage the Tkinter GUI framework for Python. However, the GUI slows down development time tremendously. A CLI is much easier to work with.


## Setup Information

### Requirements
- Python3
- python3-virtualenv
- python3-pip

### Local Setup
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

#### Editing code 

There will be some filepaths to adjust in the code based on your machine.

The first is in `src/db/__init__.py` and is the `DATABASE_DIRECTORY`
For example mine is edited to be 

```python
# setup database master file
DATABASE_DIRECTORY = "C:/Users/ander/OneDrive/Code/python/financial_analyzer_CLI/src/db/financials.db" # tag:hardcode
```

The second is in the monthly statements base filepath

#### Running application

4. Run the application:
    ```bash
    python src/main.py
    ```
    
### Financial Data File Structure

On my computer I have a folder where I store all the statements for each account. Each month
I go to the accounts and download a file representing all the account information for each
month. Typically, this is .csv format. The file structure for the data looks like:

For example - all under "C:\Users\anders\Documents\Financials\"

- monthly_statements\2020\
    - 01-January\
    - 02-February\
    - ...
    - 12-December
- monthly_statements\2021\
    - 01-January\
    - ...
    - 12-December\

And so on for as many years as you want to create.


## How to load in data in application

1.	Upon running `python main.py` - will be presented with main menu
2.	Press `4` and enter for the "Load Data" menu.
3.	Enter `1` in the keyboard to load in data from certain year/month
4.	You will be prompted for the date to locate the correct folder path.
5.	After finding file in folder path, loading will begin!


## Resources

### General
- [Financial Budget Analysis with Python - thecleverprogrammer.com](https://thecleverprogrammer.com/2021/04/05/financial-budget-analysis-with-python/)

### Graphing
- [Funnel charts with plotly](https://plotly.com/python/funnel-charts/)

### Other Budget Trackers
- [Ledger CLI](https://www.ledger-cli.org/)
- [hledger](https://hledger.org/)
- 



>>>>>>> main
