

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