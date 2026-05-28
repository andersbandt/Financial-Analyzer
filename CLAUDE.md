# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Financial-Analyzer is a personal finance management application with two entry points: a CLI for data loading/categorization and a Dash web dashboard for visualization. It loads transaction data from CSV/PDF financial statements, categorizes transactions automatically via keywords or ML, and provides analysis tools for spending history, budgeting, and investment tracking.

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

### Start the Dashboard
```bash
python src/dashboard.py
# Opens at http://127.0.0.1:8050
```

The CLI is unchanged — use it for loading data, categorizing transactions, and account management. The dashboard is read-only visualization.

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
    |
Statement Classes (parse raw data)
    |
Transaction Objects
    |
Ledger (collection of transactions)
    |
Categorization (automatic via keywords/ML or manual)
    |
SQLite Database (persistence)
    |
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
  - Account types: 1=Saving, 2=Checking, 3=Credit, 4=Investment
- `category`: Hierarchical categories (category_id, parent_id, name)
- `keywords`: Category keywords for auto-classification
- `budget`: Category spending/savings limits
- `balance`: Historical account balance snapshots
- `investment`: Investment-specific transactions (ticker, shares, value, trans_type)
- `ticker_metadata`: Ticker asset type cache (ticker, asset_type, name, last_updated)
  - asset_type values: EQUITY, ETF, MUTUALFUND, BOND, MONEYMARKET, CRYPTOCURRENCY, UNKNOWN
  - Updated via CLI Investments tab or dashboard Ticker Type Manager

**Helper Tables:**
- `file_mapping`: Maps file search strings to account_ids for automatic file-to-account matching
- `file_history`: Tracks loaded statement files to prevent duplicates
- `goals`: Account-specific savings goals

Access via helper modules in `src/db/helpers/` (transactions.py, account.py, category.py, investments.py, ticker_metadata.py, etc.)

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

### Investment Helper (`src/analysis/investment_helper.py`)

Key concepts for working with investment data:

**Price resolution order** (both `InvestmentTransaction.__init__` and `get_ticker_price()`):
1. Manual override (`src/db/price_override.json`) — user-set, highest priority
2. In-memory price cache (`_PRICE_CACHE`) — populated from `price_cache.json` on first use
3. Live API fetch (Finnhub → yfinance → yahoo_fin → yfinance history) — only when `live_price=True`

**Asset type resolution order** (`InvestmentTransaction.__init__` with `live_price=False`):
1. `_ASSET_TYPE_CACHE` (in-memory, cleared by `refresh_asset_type_cache()`)
2. `dbh.ticker_metadata.get_ticker_asset_type(ticker)` (DB)
3. Falls back to `"UNKNOWN"`

**Key functions:**
- `get_all_active_ticker(live_price=False)` — returns net-positive-share positions as `InvestmentTransaction` objects
- `refresh_asset_type_cache()` — clears `_ASSET_TYPE_CACHE` so next call re-reads from DB
- `set_manual_price_override(ticker, price)` — writes to `price_override.json`
- `get_ticker_cost_basis(account_id, ticker)` in `db/helpers/investments.py` — returns `(avg_cost_per_share, first_buy_date)` from BUY transactions

**Caching files** (in `src/db/`, gitignored):
- `price_cache.json` — persists fetched prices between restarts; format `{ticker: {price, date}}`
- `price_override.json` — manual price overrides; format `{ticker: {price}}`

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

# Investments
dbh.ticker_metadata.upsert_ticker_asset_type(ticker, asset_type)  # safe insert-or-update
dbh.investments.get_ticker_cost_basis(account_id, ticker)  # returns (avg_cost, first_buy_date)
```

### CLI Interaction Helpers

Located in `src/cli/cli_helper.py`:
- `promptYesNo(prompt)`: Yes/No confirmation
- `spinput(prompt, inp_type="int")`: Type-validated input
- `get_account_id_manual()`: Interactive account selector

## Dash Web Dashboard

### File Structure
```
src/
  dashboard.py        <- entry point (db_init + app.run)
  web/
    __init__.py
    app.py            <- Dash layout, callbacks, create_app() -- tab-based UI
    charts.py         <- all Plotly figure builders + data helpers
```

### UI Structure (Tabs)
The dashboard is organized into 8 tabs via `dcc.Tabs`. Each tab has a persistent URL (`/#tabname`) — navigating to `http://127.0.0.1:8050/#investments` opens directly to the Investments tab and the selection survives page refresh.

1. **Overview** — Period selector + KPI cards (net worth, this month's spend, savings rate) + period summary KPIs (income/expenses/delta/count) + spending pie + monthly stacked bar
2. **Spending** — Month-over-month vs baseline, category drill-down, Sankey flow (with its own `dcc.DatePickerRange` + quick-set dropdown)
3. **Income & Savings** — Period selector + income vs expenses grouped bar with savings rate line + net savings bars with cumulative line
4. **Balances** — Simple asset allocation pie + wealth breakdown table, balance over time (by-account + by-type, with its own days/bins controls), single account day-by-day, recorded balance ledger
5. **Retirement** — Monte Carlo with 7 number-input fields (current age, retirement age, death age, return mean/stddev, inflation mean/stddev) + "Run simulation" button (uses `State`)
6. **Investments** — Three allocation pies (high-level, equity breakdown, per-ticker) + Ticker Type Manager + Manual Price Overrides + Portfolio Positions table + Investment Transactions table
7. **Categories** — Plotly treemap of the category hierarchy + indented text printout listing every category with its `id → parent_id` mapping and keyword list
8. **Transactions** — Multi-filter search (keyword + date range + category +/- descendants + account + amount min/max), largest transactions, month review

Each tab's content is built by a `_*_tab()` helper function inside `app.py`. **There is no global period selector** — each tab/section owns its own period or date controls.

### Investments Tab Details

The Investments tab has several distinct sections:

**Asset Allocation Pies** (three charts):
- *High-level*: Stocks / Bonds / Cash / Crypto. Cash always includes savings+checking DB balances. Investment positions use `market_value` when available (live or cached price), falling back to `avg_cost * shares` so all positions show even without a price refresh.
- *Equity breakdown*: Splits equity-type holdings into Individual Stocks / ETFs / Mutual Funds. Same market_value → cost-basis fallback.
- *Per-ticker*: One slice per ticker with a distinct qualitative color palette. Same fallback logic.

**Ticker Type Manager**:
- Grid of `dcc.Dropdown` components (one per ticker) — **NOT** a DataTable. This is intentional: Dash 4's DataTable `presentation: "dropdown"` cells do not reliably update the `data` prop on selection.
- Save callback uses `State({"type": "ticker-type", "ticker": ALL}, "value")` pattern-matching to collect all dropdown values.
- On save: calls `dbh.ticker_metadata.upsert_ticker_asset_type()` for each ticker, then calls `invh.refresh_asset_type_cache()` and rebuilds the three allocation pies.
- UNKNOWN rows are highlighted with an amber background.

**Manual Price Overrides**: Ticker + price inputs; saved to `src/db/price_override.json`. Override takes highest priority in price resolution.

**Portfolio Positions table**: Columns include Avg Cost, Current Price, Market Value, Gain%, CAGR, Price Source. Gain% and CAGR are computed from `dbh.investments.get_ticker_cost_basis()` and the first buy date. `price_source` shows whether price came from live API, cache, override, or cost basis fallback.

**Investment Transactions table**: All raw investment records, filterable by type (BUY / SELL / DIV checklist).

### Standardized Period Options
All period dropdowns share a single `PERIOD_OPTIONS` list:
`3 months / 6 months / 12 months / 24 months / 5 years / All time`

The value `0` is the "All time" sentinel. In `charts.py`, `_resolve_months_prev(0)` walks back to the earliest transaction date (cached per session via `_earliest_transaction_date()`); `_period_transactions(0)` calls `recall_transaction_data()` with no date filter. The balance chart uses `BALANCE_DAYS_OPTIONS` (`180d / 1yr / 2yr / 5yr / All time`) for the same reason.

### Transaction Search Filters
The Transactions tab's search supports the same filter dimensions as the CLI's `search_05_multi_filter()` in `analysis.transaction_helper`:
- Description keyword (case-insensitive substring)
- Period dropdown (`PERIOD_OPTIONS`)
- Specific date range (`dcc.DatePickerRange`) — when both dates are set, overrides the period dropdown
- Category dropdown + "include descendants" checklist (uses `cath.get_all_category_descendants`)
- Account dropdown
- Amount min/max number inputs

`charts.get_transaction_rows()` accepts every filter as a keyword arg and applies them progressively.

### Sankey Date Selector
The Sankey diagram is date-anchored rather than period-anchored:
- `dcc.DatePickerRange` — explicit start and end dates (defaults to last 12 months on page load)
- Quick-set dropdown — picks a relative window (3mo / 6mo / 12mo / 24mo / 5y / YTD / All time) and updates the date pickers via a `sankey_quickset` callback
- Top-level vs Hierarchical view radio

### Current Charts
- **KPI cards**: Net worth (recorded DB balances), this month's spending, period savings rate
- **Period summary KPIs**: Income, expenses, net delta, and transaction count for selected period
- **Spending pie**: Top-level category breakdown for selected period
- **Monthly stacked bar**: Spending per category per month
- **Month-over-month comparison**: % delta vs N-month baseline average
- **Income vs expenses**: Grouped bar (income/expenses) + savings rate line (secondary axis)
- **Net savings**: Monthly net bars + cumulative savings line (secondary axis)
- **Asset allocation pie (Balances tab)**: Simple bucketed view (Cash / Retirement / Taxable Investment) from recorded DB balances — no live price fetch
- **Investment allocation pies (Investments tab)**: Three charts — high-level (Stocks/Bonds/Cash/Crypto), equity type breakdown (Individual Stocks/ETFs/Mutual Funds), per-ticker; all use market_value with cost-basis fallback
- **Wealth breakdown table**: Per-account balance + type + last-updated date (no live price fetch)
- **Balance over time — by account**: Stacked area of per-account balances over N time bins
- **Balance over time — by type**: Stacked area aggregated by account type (Saving / Checking / Credit / Investment)
- **Single account balance**: Day-by-day modeled balance for one selected account (falls back to raw snapshots)
- **Balance ledger table**: All recorded balance snapshots (filterable to one account via the dropdown)
- **Retirement Monte Carlo**: Histogram of simulated retirement balances with p10/p50/p90 KPI cards
- **Category drill-down**: Stacked bar of any category's subcategories over time
- **Category treemap + tree printout**: Hierarchical view of every category with id → parent_id mapping and keyword counts
- **Sankey diagram**: Spending flow — top-level or hierarchical view
- **Multi-filter transaction search**: keyword + period + date range + category (+ descendants) + account + amount min/max
- **Portfolio positions table**: Active holdings with avg cost, gain%, CAGR, price source
- **Investment transactions table**: Raw investment records with BUY/SELL/DIV filter
- **Largest transactions table**: Top N by absolute value within a configurable window
- **Month review**: Year/month picker with a transactions table + category-spending summary side-by-side

### Architecture Notes
- All charts call the existing `src/analysis/` layer unchanged — no data logic in `web/`
- `charts.py` has a per-session `_cat_name_cache` dict, plus `_earliest_txn_date` and `_earliest_balance_date` caches so "All time" lookups don't re-scan the full DB every callback
- Every chart builder that takes a `months_prev` accepts `0` as the "all time" sentinel
- Net worth KPI and Balances-tab allocation pie deliberately use `dbh.balance.get_recent_balance()` directly (not `balh.get_account_balance`) to skip live investment price fetches on page load
- Retirement Monte Carlo lives behind an explicit "Run simulation" button (uses `State`, not `Input`) so users can tune parameters without retriggering 5k+ simulations on every keystroke
- Tabs are rendered eagerly (content lives inside each `dcc.Tab`'s children) — all tab callbacks fire on initial page load, which is acceptable for this read-only DB-backed app
- URL routing: `dcc.Location` + a single `sync_tab_url` callback keeps `main-tabs.value` and `url.hash` in sync. Uses `ctx.triggered_id` + `no_update` to prevent circular callbacks
- `dash` added to `requirements.txt`

### Dash 4 Gotchas
Running Dash 4.0.0 — several breaking changes from 2.x to be aware of:

- **Duplicate outputs require `allow_duplicate=True`**: If two callbacks write to the same `Output`, Dash 4 will silently drop ALL callbacks (not just the duplicate) unless you add `allow_duplicate=True` to the `Output(...)` calls on the secondary callback. This is a silent failure that's very hard to debug.
- **DataTable `presentation: "dropdown"` broken in Dash 4**: Selecting from a dropdown cell does not update the `data` prop. Do not use this pattern. Use individual `dcc.Dropdown` components with pattern-matching IDs (`{"type": "...", "key": value}`) and `State(..., ALL, ...)` in callbacks instead.
- **`dash_table` is now `dash.dash_table`**: No separate package — import `dash_table` from `dash` directly: `from dash import dash_table`.

### Dashboard TODO
Roughly in priority order:

**Medium effort:**
- [ ] **International vs US diversification** — chart or KPI showing % of equity holdings that are US-domestic vs international (e.g. VXUS); would need a domestic/international tag per ticker in `ticker_metadata` or a manual classification
- [ ] **Ticker detail page** — drilldown for a single ticker: metadata, price history, position history over time
- [ ] **Live asset allocation with Refresh** — hook the Investments tab allocation pies to a "Refresh (Live Prices)" button so clicking Refresh updates the pies with live data (currently they always use cached/cost-basis)

**Polish:**
- [ ] Dark mode toggle
- [ ] Persist period/dropdown selections across page refreshes via `dcc.Store` (tab selection is already persisted via URL hash; this is for per-tab controls like the period dropdown)
- [ ] Make the transaction table link back to CLI (e.g. copy sql_key for `a07_add_note`)
- [ ] Calendar heatmap of daily spending (GitHub-style grid)
- [ ] Top merchants chart (group by extracted merchant name)
- [ ] Year-over-year comparison (pick two date ranges, view deltas side-by-side)

**Shipped (recent sessions):**
- [x] **URL tab routing** — `dcc.Location` + `sync_tab_url` callback; each tab has a hash URL (`/#investments` etc.) that persists on refresh and works with browser back/forward
- [x] **Ticker Type Manager** — per-ticker `dcc.Dropdown` grid (replaced broken DataTable dropdown); Save button uses pattern-matching `ALL` callback to reliably persist types to `ticker_metadata`
- [x] **Asset allocation consistency** — all three investment pies now use the same valuation logic (market_value when available, avg_cost * shares fallback), so totals match across charts
- [x] **Investment allocation pies** — three charts in Investments tab: high-level (Stocks/Bonds/Cash/Crypto), equity type breakdown, per-ticker with distinct colors
- [x] **Gain% and CAGR columns** — computed from `get_ticker_cost_basis()` (actual buy history), not from the position's recorded value
- [x] **Manual price overrides** — `price_override.json` + UI in Investments tab; overrides take priority over cached/live prices
- [x] **Session price caching** — `price_cache.json` persists fetched prices across restarts; page load shows cached prices without a Refresh click
- [x] **Net savings line chart** — monthly net bars + cumulative line in Income & Savings tab
- [x] **Investments tab** — positions table + all transactions with BUY/SELL/DIV type filter
- [x] **Balance tab account filter** — multi-select account picker + "Investment accounts only" toggle
- [x] **Categories tab** — Plotly treemap + indented text printout of category hierarchy
- [x] **Multi-filter transaction search** — port of CLI `search_05_multi_filter`
- [x] **Sankey date selector** — `dcc.DatePickerRange` + quick-set dropdown
- [x] **Per-tab period selectors** — removed global "Period" dropdown
- [x] **Retirement: sliders → number inputs**
- [x] **Tabbed UI** — 8 tabs replacing long-scroll layout
- [x] **Standardized period dropdowns** — shared `PERIOD_OPTIONS` list

## Known Limitations & TODOs

- **Categories tab partially broken**: The category tree text printout (`get_category_tree_text` in `web/charts.py`) can still render incorrectly for some edge cases. The `id=0` "NA" placeholder category (with `parent_id=0`, self-referential) is now filtered out before tree-walking, which fixed the RecursionError, but the overall hierarchy rendering may still have issues with other edge cases.
- **Hardcoded file paths and account mappings**: See `# tag:hardcode` comments throughout; notably in `db/__init__.py`, `cli/cli_main.py`, `tools/load_helper.py`, and `analysis/investment_helper.py`
- **ML categorization model not actively used**: Commented out in some flows; ~70% accuracy on 60-class classification
- **Test coverage is minimal**: `tests/tester.py` is primarily for experimentation
- **No API integration**: All data is manually downloaded CSV/PDF (no Plaid, no bank APIs)
- **Duplicate prevention not foolproof**: Some duplicate transactions may slip through
- **CLI command REPL (future)**: Replace or augment top-level arrow-key menu with a typed command prompt (`load`, `search`, `balance`, etc.) backed by `prompt_toolkit` autocomplete

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

**5. Feature Engineering**
- Extract merchant names from descriptions (regex patterns)
- Add time-of-day features if available
- Create account-category interaction features

**Current Model Features:**
- Text: TF-IDF on transaction descriptions (trigrams, 3000 features)
- Numeric: value, AccountType, Month, Day, DayOfWeek, IsWeekend, AmountBucket
- Class balancing enabled (`class_weight='balanced'`)
