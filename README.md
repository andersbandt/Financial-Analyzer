# Financial-Analyzer
Analyzes spending, budget, and investment data in a GUI



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
- **trans_description**    VARCHAR item with 200 character max. Represents a description of the transaction.

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


## Description of MAIN functions

### graphing_analyzer.py (analyzing)

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



## Budget Analysis Workings

Budget analysis will be based on the Category objects created in the Tree.

There will have to be some error handling to determine if the sum of all children is greater than the 
cap of the parent budget.

For software implementation, might want to make Budget a subcategory of Category?


## Things to Work On

### Code Cleanup

One thing to add to make the code prettier is to create a general class for data adding. Notice that I use a very similar 
layout for adding a Category, keyword, budget category. I could create a general class for that.



## Resources

- [Financial Budget Analysis with Python - thecleverprogrammer.com](https://thecleverprogrammer.com/2021/04/05/financial-budget-analysis-with-python/)





