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
#### Local data option
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

#### Cloud based
In the future some integration with an API such as Plaid would ease user access

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



