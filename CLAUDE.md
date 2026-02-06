# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Financial-Analyzer is a CLI-based personal finance management application built with Python. It loads transaction data from CSV/PDF financial statements, categorizes transactions automatically via keywords or ML, and provides analysis tools for spending history, budgeting, and investment tracking.

## Environment Setup

1. Create and activate virtual environment:
```bash
virtualenv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure hardcoded paths (see Hardcoded Configuration section below)

## Running the Application

### Start the CLI application
```bash
python src/main.py
```

The application will:
- Initialize the SQLite database if it doesn't exist (creates tables, adds seed data)
- Launch the main menu with 9 tabs for different functionality

### Running Tests
```bash
python tests/tester.py
```

Note: Test coverage is minimal and primarily used for experimentation.

## Hardcoded Configuration

**CRITICAL**: Before running, update these hardcoded paths in the source code:

1. **Database path** in `src/db/__init__.py` (line 6):
```python
DATABASE_DIRECTORY = "C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/financials.db"
```

2. **Statements base path** in `src/cli/cli_main.py` (line 22):
```python
self.basefilepath = "C:/Users/ander/OneDrive/Documents/Financials"
```

Look for `# tag:hardcode` or `# tag:HARDCODE` comments throughout the codebase to find other hardcoded paths.

## Architecture

### Core Data Flow

```
Financial Statements (CSV/PDF)
    ↓
Statement Classes (parse raw data)
    ↓
Transaction Objects
    ↓
Ledger (collection of transactions)
    ↓
Categorization (automatic via keywords/ML or manual)
    ↓
SQLite Database (persistence)
    ↓
Analysis & Visualization
```

### Key Classes & Their Relationships

**Transaction** (`src/statement_types/Transaction.py`)
- Represents a single financial transaction
- Fields: date, account_id, category_id, value, description, note, sql_key
- Handles automatic categorization via keyword matching

**Ledger** (`src/statement_types/Ledger.py`)
- Collection of Transaction objects
- Provides methods for sorting, categorization, printing, and persistence
- Can categorize transactions via: keywords, ML model, or manual CLI input

**Statement** (`src/statement_types/Statement.py`)
- Extends Ledger
- Represents monthly statement from a specific account
- Abstract `load_statement_data()` method implemented by account-specific subclasses

**Account-specific Statement Classes** (`src/statement_types/`)
- Each financial institution has a custom parser (e.g., `Marcus.py`, `ChaseCard.py`, `VanguardRoth.py`)
- Most extend `csvStatement.py` with custom column mappings
- Investment accounts use `Investment.py` base class

### Database Schema

SQLite database defined in `src/db/__init__.py` and documented in `src/db/README.md`:

**Core Tables:**
- `transactions`: All financial transactions (date, account_id, category_id, amount, description, note)
- `account`: Account metadata (name, institution, type, balance, retirement status)
- `category`: Hierarchical categories (category_id, parent_id, name)
- `keywords`: Category keywords for auto-classification
- `budget`: Category spending/savings limits
- `balance`: Historical account balance snapshots
- `investment`: Investment-specific transactions (ticker, shares, value)

**Helper Tables:**
- `file_mapping`: Maps file search strings to account_ids for automatic file-to-account matching
- `file_history`: Tracks loaded statement files to prevent duplicates
- `goals`: Account-specific savings goals

Access via helper modules in `src/db/helpers/` (transactions.py, account.py, category.py, etc.)

### CLI Structure

**Main Menu** (`src/cli/cli_main.py`)
- Tab-based navigation system (9 tabs)
- Each tab is a SubMenu with multiple Action items
- Uses `cli_class.py` SubMenu/Action pattern

**Tab Organization:**
1. Dashboard - Overview of financial status
2. Manage Categories - Create/edit/delete categories and keywords
3. Manage Accounts - Account CRUD operations
4. Load Data - Import monthly statements from filesystem
5. Analyze Spending History - Time-series spending analysis, category breakdowns
6. Balances - Account balance tracking and retirement modeling
7. Categorize Transactions - Manual transaction categorization interface
8. Budgeting - Budget creation and tracking
9. Investments - Investment portfolio analysis

Each tab in `src/cli/tabs/` follows the pattern of returning an Action array to populate its submenu.

### Transaction Categorization System

Three categorization methods (in `Ledger.categorizeStatementAutomatic()`, `categorize_manual()`, `categorize_ml()`):

1. **Keyword-based**: Matches transaction descriptions against keywords table
   - Keywords stored in `keywords` SQL table (category_id, keyword)
   - Case-insensitive substring matching
   - First match wins (order matters)

2. **ML-based** (`src/analysis/transaction_classifier.py`):
   - Scikit-learn pipeline with TF-IDF on descriptions + numerical features
   - LogisticRegression multi-class classifier
   - Features: description (text), value, account type, day of month, day of week
   - Model persisted via joblib to `analysis/model.joblib`

3. **Manual**: Interactive CLI prompts user to select category per transaction

### File Loading System

**File Discovery** (`src/tools/load_helper.py`):
- Expected folder structure: `{basefilepath}/{year}/monthly_statements/{month}/`
- Months formatted as `01-January/`, `02-February/`, etc.
- `get_year_month_files()` scans directory for statement files

**Account Matching**:
- `match_file_to_account()` uses `file_mapping` table to match filename patterns to account_ids
- Returns None if no mapping found (file skipped unless manual prompt enabled)

**Statement Creation**:
- `create_statement()` contains hardcoded account_id-to-Statement-class mapping
- Each account type instantiates appropriate parser (Marcus, csvStatement, VanguardBrokerage, etc.)
- CSV parsers require column indices: date_col, amount_col, description_col

**Loading Process**:
- `get_month_year_statement_list()` is the main orchestration function
- For each file: creates Statement → calls `load_statement_data()` → prints status table
- Returns list of Statement objects ready for categorization and saving

### Analysis & Visualization

**Modules:**
- `src/analysis/transaction_helper.py`: Transaction filtering and aggregation utilities
- `src/analysis/balance_helper.py`: Account balance calculations
- `src/analysis/investment_helper.py`: Investment returns and portfolio analysis
- `src/analysis/graphing/`: Plotly-based visualizations (time series, category breakdowns, Sankey diagrams)

**Common Patterns:**
- Use `transaction_recall.py` for querying transactions by date ranges and categories
- Category analysis respects parent-child relationships (defined in `category.parent_id`)
- Investment data pulls from separate `investment` table, not `transactions`

### Logging

Uses `loguru` library with colored module-based logging:
- Configured in `src/main.py` with per-module color assignment
- Log level controlled via `level` variable in `main()` (default: DEBUG)

## Common Development Patterns

### Adding a New Account Type

1. Create parser class in `src/statement_types/` (extend `csvStatement` or `Investment`)
2. Add account to `account` table via SQL or CLI (Tab 3)
3. Add file mapping pattern to `file_mapping` table
4. Update `create_statement()` hardcode in `src/tools/load_helper.py` with account_id mapping
5. Test by loading a statement file via CLI (Tab 4)

### Adding Transaction Categories

Categories are hierarchical (parent_id references another category_id):
- Root categories have parent_id = 1
- Use CLI Tab 2 to create categories and associate keywords
- Keywords should be uppercase substrings commonly found in merchant descriptions

### Database Queries

Import db helpers: `import db.helpers as dbh`

Common operations:
```python
# Transactions
dbh.transactions.insert_transaction(transaction_obj)
dbh.transactions.get_transaction(transaction_obj)  # Check if exists
dbh.transactions.update_transaction_category(transaction_obj)

# Accounts
dbh.account.get_account_name_from_id(account_id)
dbh.account.get_all_accounts()

# Categories
dbh.category.get_category_name_from_id(category_id)
cath.category_id_to_name(category_id)  # From categories_helper
```

### CLI Interaction Helpers

Located in `src/cli/cli_helper.py`:
- `promptYesNo(prompt)`: Yes/No confirmation
- `spinput(prompt, inp_type="int")`: Type-validated input
- `get_account_id_manual()`: Interactive account selector

## Known Limitations & TODOs

- Hardcoded file paths and account mappings (see tags in code)
- ML categorization model not actively used (commented out in some flows)
- Test coverage is minimal
- No API integration (Plaid, bank APIs) - all data is manually downloaded CSV/PDF
- Some duplicate prevention logic exists but is not foolproof
- Investment tracking is basic compared to transaction tracking

## ML Model Improvements (Future Work)

Current ML model (`src/analysis.py` + `src/analysis/transaction_classifier.py`) achieves ~70% accuracy on 60-class classification with ~4,500 transactions. This is challenging due to:
- Small dataset size (75 transactions per category average)
- High class imbalance (some categories have only 1-3 samples)
- Similar/overlapping categories (EATING OUT vs FAST FOOD vs BARS)

### Recommended Improvements:

**1. Hierarchical Classification (Highest Impact)**
- Implement 2-stage model: Top-level categories (Food, Transport, Bills) → Sub-categories
- Expected improvement: 85%+ accuracy on top-level, easier to maintain
- Requires: Restructure category table to explicit hierarchy levels

**2. Hybrid Keyword + ML Approach**
- Use keyword rules for high-confidence cases (~90% of transactions)
- Reserve ML for ambiguous cases only (~10%)
- Current keyword system in `Ledger.categorizeStatementAutomatic()` could be primary classifier

**3. Category Consolidation**
- Merge rare categories (<10 samples) into "OTHER" or parent categories
- Combine similar categories (EATING OUT + FAST FOOD + BARS → DINING)
- Reduces complexity, improves model performance

**4. Alternative Models**
- Try Random Forest or XGBoost (often better than LogisticRegression for tabular data)
- Consider ensemble methods combining multiple models
- Experiment with deep learning (transformers) if dataset grows significantly

**5. Feature Engineering**
- Extract merchant names from descriptions (regex patterns)
- Add time-of-day features if available
- Create account-category interaction features

**Current Model Features:**
- Text: TF-IDF on transaction descriptions (trigrams, 3000 features)
- Numeric: value, AccountType, Month, Day, DayOfWeek, IsWeekend, AmountBucket
- Class balancing enabled (`class_weight='balanced'`)

See `/tmp/claude.../scratchpad/ML_IMPROVEMENTS_SUMMARY.md` for detailed recent improvements.
