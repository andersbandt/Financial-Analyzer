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

4. Run the application:
    ```bash
    python3 src/main.py
    ```
    
### Financial Data File Structure

On my computer I have a folder where I store all the statements for each account. Each month
I go to the accounts and download a file representing all the account information for each
month. Typically, this is .csv format. The file structure for the data looks like:

For example - all under "C:\Users\ander\Documents\Financials\"

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



