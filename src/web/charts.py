"""
web/charts.py — Plotly figure builders for the Financial Dashboard.

Each build_* function returns a go.Figure. compute_kpis() returns a plain
dict of scalar values for the KPI card row.
"""

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import datetime as _dt

import db.helpers as dbh
import categories.categories_helper as cath
from account import account_helper as acch
from analysis import analyzer_helper as anah
from analysis import investment_helper as invh
from analysis.graphing import graphing_helper as grah
from analysis.data_recall import transaction_recall as transr
from analysis import balance_helper as balh
from tools import date_helper as dateh

# Categories whose transactions should be excluded from income/expense charts.
# These are accounting transfers, not real cashflow.
_SKIP_CATS = {"BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"}

# Simple per-session cache so repeated chart builds don't hammer the DB.
_cat_name_cache: dict[int, str] = {}

# Cached earliest dates so "all time" lookups don't re-scan the full DB every callback.
_earliest_txn_date: str | None = None
_earliest_balance_date: str | None = None


def _cat_name(cat_id: int) -> str:
    if cat_id not in _cat_name_cache:
        _cat_name_cache[cat_id] = cath.category_id_to_name(cat_id)
    return _cat_name_cache[cat_id]


def _earliest_transaction_date() -> str | None:
    """YYYY-MM-DD of the oldest transaction in the DB. Cached per session."""
    global _earliest_txn_date
    if _earliest_txn_date is None:
        txns = transr.recall_transaction_data()
        if not txns:
            return None
        _earliest_txn_date = min(t.date for t in txns)
    return _earliest_txn_date


def _earliest_balance_date_str() -> str | None:
    global _earliest_balance_date
    if _earliest_balance_date is None:
        rows = dbh.balance.get_balance_ledge_data()
        if not rows:
            return None
        _earliest_balance_date = min(r[3] for r in rows)
    return _earliest_balance_date


def _resolve_months_prev(months_prev: int) -> int:
    """
    Convert 0 (the 'All time' sentinel) into the actual number of months
    from today back to the earliest transaction. Returns the original value otherwise.
    """
    if months_prev and months_prev > 0:
        return months_prev
    earliest = _earliest_transaction_date()
    if not earliest:
        return 12  # nothing in DB — graceful default
    yr, mo, _ = dateh.get_date_int_array()
    eyr, emo = int(earliest[:4]), int(earliest[5:7])
    return max((yr - eyr) * 12 + (mo - emo) + 1, 1)


def _resolve_balance_days(days_prev: int) -> int:
    """Convert 0 (the 'All time' sentinel) into days from today back to earliest balance snapshot."""
    if days_prev and days_prev > 0:
        return days_prev
    from datetime import datetime
    earliest = _earliest_balance_date_str()
    if not earliest:
        return 365
    try:
        delta = datetime.now() - datetime.strptime(earliest, "%Y-%m-%d")
        return max(int(delta.days) + 1, 30)
    except ValueError:
        return 365


def _period_transactions(months_prev: int):
    """Fetch transactions for the selected period; 0 means all-time (no date filter)."""
    if not months_prev or months_prev <= 0:
        return transr.recall_transaction_data()
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    return transr.recall_transaction_data(date_start, date_end)


def _period_label(months_prev: int) -> str:
    """Human-readable label for a period selection (used in chart titles)."""
    if not months_prev or months_prev <= 0:
        return "all time"
    if months_prev % 12 == 0 and months_prev >= 12:
        years = months_prev // 12
        return f"last {years} year{'s' if years != 1 else ''}"
    return f"last {months_prev} months"


def _month_series(months_prev: int):
    """Return (labels, [(year, month), ...]) for the last months_prev months.
    months_prev=0 resolves to the full history back to the earliest transaction."""
    months_prev = _resolve_months_prev(months_prev)
    yr, mo, _ = dateh.get_date_int_array()
    oldest_mo = mo - months_prev + 1
    oldest_yr = yr
    while oldest_mo < 1:
        oldest_mo += 12
        oldest_yr -= 1

    labels, pairs = [], []
    y, m = oldest_yr, oldest_mo
    for _ in range(months_prev):
        labels.append(f"{y}-{m:02d}")
        pairs.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return labels, pairs


def _income_expense_split(transactions):
    """Return (income, expenses) totals for a transaction list, skipping transfer categories."""
    income = expenses = 0.0
    for t in transactions:
        if _cat_name(t.category_id) in _SKIP_CATS:
            continue
        if t.value > 0:
            income += t.value
        else:
            expenses += abs(t.value)
    return income, expenses


# ─── Spending overview ────────────────────────────────────────────────────────

def build_spending_pie(months_prev: int) -> go.Figure:
    transactions = _period_transactions(months_prev)

    if not transactions:
        fig = go.Figure()
        fig.update_layout(title="No transactions found for this period")
        return fig

    categories = cath.load_categories()
    cat_names, amounts = anah.create_top_category_amounts_array(transactions, categories, count_NA=False)
    cat_names, amounts = grah.strip_non_expense_categories(cat_names, amounts)
    cat_names, amounts = grah.strip_zero_categories(cat_names, amounts)
    amounts = grah.format_expenses(amounts)

    total = sum(amounts)
    fig = go.Figure(go.Pie(
        labels=cat_names,
        values=amounts,
        hole=0.3,
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
        textinfo="percent",
        textposition="inside",
    ))
    fig.update_layout(
        title=f"Spending breakdown — {_period_label(months_prev)}  (${total:,.0f} total)",
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=20, l=20, r=160),
        height=480,
    )
    return fig


def build_monthly_bar(months_prev: int) -> go.Figure:
    labels, pairs = _month_series(months_prev)
    date_bin_trans = [transr.recall_transaction_month_bin(y, m) for y, m in pairs]
    bin_dicts = anah.gen_bin_analysis_dict(date_bin_trans)

    if not bin_dicts or not bin_dicts[0]["categories"]:
        fig = go.Figure()
        fig.update_layout(title="No category data found")
        return fig

    cat_names = bin_dicts[0]["categories"]
    cat_amounts = {cat: [abs(d["amounts"][i]) for d in bin_dicts]
                   for i, cat in enumerate(cat_names)}
    cat_names_sorted = sorted(cat_names, key=lambda c: sum(cat_amounts[c]), reverse=True)

    fig = go.Figure()
    for cat in cat_names_sorted:
        fig.add_trace(go.Bar(
            name=cat,
            x=labels,
            y=cat_amounts[cat],
            hovertemplate=f"<b>{cat}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title=f"Monthly spending — {_period_label(months_prev)}",
        yaxis=dict(tickprefix="$", tickformat=","),
        xaxis=dict(tickangle=-45),
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=80, l=60, r=160),
        height=480,
    )
    return fig


def build_mom_comparison(baseline_months: int) -> go.Figure:
    yr, mo, _ = dateh.get_date_int_array()

    prev_yr, prev_mo = dateh.get_previous_month(yr, mo)
    prev_trans = []
    for _ in range(12):
        prev_trans = transr.recall_transaction_month_bin(prev_yr, prev_mo)
        if prev_trans:
            break
        prev_yr, prev_mo = dateh.get_previous_month(prev_yr, prev_mo)

    if not prev_trans:
        fig = go.Figure()
        fig.update_layout(title="No recent transaction data found")
        return fig

    # Resolve the all-time sentinel into a concrete month count ending at prev_yr/prev_mo
    baseline_months = _resolve_months_prev(baseline_months)

    base_end_mo = prev_mo - 1
    base_end_yr = prev_yr
    while base_end_mo < 1:
        base_end_mo += 12
        base_end_yr -= 1

    base_start_mo = base_end_mo - baseline_months + 1
    base_start_yr = base_end_yr
    while base_start_mo < 1:
        base_start_mo += 12
        base_start_yr -= 1

    start_range = dateh.month_year_to_date_range(base_start_yr, base_start_mo)
    end_range = dateh.month_year_to_date_range(base_end_yr, base_end_mo)
    baseline_trans = transr.recall_transaction_data(start_range[0], end_range[1])

    categories = cath.load_categories()
    cat_names, prev_amounts = anah.create_top_category_amounts_array(prev_trans, categories, count_NA=False)
    _, baseline_amounts = anah.create_top_category_amounts_array(baseline_trans, categories, count_NA=False)

    orig = cat_names[:]
    cat_names, prev_amounts = grah.strip_non_expense_categories(orig, prev_amounts)
    _, baseline_amounts = grah.strip_non_expense_categories(orig, baseline_amounts)

    baseline_avg = [abs(x) / baseline_months for x in baseline_amounts]
    prev_abs = [abs(x) for x in prev_amounts]

    pct_diffs = []
    for prev, base in zip(prev_abs, baseline_avg):
        if base == 0:
            pct_diffs.append(100.0 if prev > 0 else 0.0)
        else:
            pct_diffs.append(((prev - base) / base) * 100)

    colors = ["#e05252" if d > 0 else "#52a852" for d in pct_diffs]

    fig = go.Figure(go.Bar(
        x=pct_diffs,
        y=cat_names,
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>%{x:+.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=f"vs {baseline_months}-month avg — {prev_yr}-{prev_mo:02d}  (red = over avg)",
        xaxis=dict(ticksuffix="%", zeroline=True, zerolinewidth=2, zerolinecolor="#888"),
        margin=dict(t=60, b=40, l=160, r=40),
        height=max(300, len(cat_names) * 24 + 80),
    )
    return fig


# ─── Income & savings ─────────────────────────────────────────────────────────

def compute_kpis(months_prev: int) -> dict:
    """
    Returns scalars for the KPI card row.

    Net worth uses only DB-recorded balances (no live price fetch) so the
    page loads fast regardless of whether investment APIs are reachable.
    """
    # Net worth — sum latest DB balance for every account
    net_worth = sum(
        dbh.balance.get_recent_balance(acc_id) or 0
        for acc_id in dbh.account.get_all_account_ids()
    )

    # This month's spending — walk back until we find a month with data
    yr, mo, _ = dateh.get_date_int_array()
    period_label = f"{yr}-{mo:02d}"
    month_trans = []
    for _ in range(6):
        month_trans = transr.recall_transaction_month_bin(yr, mo)
        if month_trans:
            period_label = f"{yr}-{mo:02d}"
            break
        yr, mo = dateh.get_previous_month(yr, mo)

    monthly_spend = sum(
        abs(t.value) for t in month_trans
        if t.value < 0 and _cat_name(t.category_id) not in _SKIP_CATS
    )

    # Savings rate over the selected period (months_prev=0 → all time)
    period_trans = _period_transactions(months_prev)
    income, expenses = _income_expense_split(period_trans)
    savings_rate = ((income - expenses) / income * 100) if income > 0 else 0.0

    return {
        "net_worth": net_worth,
        "monthly_spend": monthly_spend,
        "savings_rate": savings_rate,
        "period_label": period_label,
    }


def build_income_vs_expenses(months_prev: int) -> go.Figure:
    """
    Grouped bar (income green, expenses red) per month with a savings-rate
    percentage line on the secondary y-axis.
    """
    labels, pairs = _month_series(months_prev)

    income_arr, expense_arr, rate_arr = [], [], []
    for y, m in pairs:
        transactions = transr.recall_transaction_month_bin(y, m)
        income, expenses = _income_expense_split(transactions)
        income_arr.append(income)
        expense_arr.append(expenses)
        rate_arr.append(((income - expenses) / income * 100) if income > 0 else 0.0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        name="Income",
        x=labels,
        y=income_arr,
        marker_color="#52a852",
        hovertemplate="<b>Income</b><br>%{x}: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        name="Expenses",
        x=labels,
        y=expense_arr,
        marker_color="#e05252",
        hovertemplate="<b>Expenses</b><br>%{x}: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        name="Savings Rate",
        x=labels,
        y=rate_arr,
        mode="lines+markers",
        line=dict(color="#4466cc", width=2),
        hovertemplate="<b>Savings Rate</b><br>%{x}: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)

    fig.update_layout(
        barmode="group",
        title=f"Income vs Expenses — {_period_label(months_prev)}",
        xaxis=dict(tickangle=-45),
        margin=dict(t=60, b=80, l=60, r=60),
        height=500,
        legend=dict(orientation="h", x=0, y=1.08),
    )
    fig.update_yaxes(tickprefix="$", tickformat=",", secondary_y=False)
    fig.update_yaxes(ticksuffix="%", title_text="Savings Rate", secondary_y=True)
    return fig


def build_net_savings(months_prev: int) -> go.Figure:
    """
    Per-month net savings (income − expenses) as green/red bars, with a
    cumulative running-total line on the secondary axis.
    """
    labels, pairs = _month_series(months_prev)

    net_arr, cumulative = [], []
    running = 0.0
    for y, m in pairs:
        transactions = transr.recall_transaction_month_bin(y, m)
        income, expenses = _income_expense_split(transactions)
        net = income - expenses
        net_arr.append(net)
        running += net
        cumulative.append(running)

    colors = ["#52a852" if n >= 0 else "#e05252" for n in net_arr]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        name="Monthly Net",
        x=labels,
        y=net_arr,
        marker_color=colors,
        hovertemplate="<b>Monthly Net</b><br>%{x}: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        name="Cumulative",
        x=labels,
        y=cumulative,
        mode="lines+markers",
        line=dict(color="#4466cc", width=2),
        marker=dict(size=5),
        hovertemplate="<b>Cumulative</b><br>%{x}: $%{y:,.0f}<extra></extra>",
    ), secondary_y=True)

    fig.update_layout(
        title=f"Net savings per month — {_period_label(months_prev)}",
        xaxis=dict(tickangle=-45),
        margin=dict(t=60, b=80, l=60, r=60),
        height=460,
        legend=dict(orientation="h", x=0, y=1.08),
    )
    fig.update_yaxes(tickprefix="$", tickformat=",", title_text="Monthly Net", secondary_y=False)
    fig.update_yaxes(tickprefix="$", tickformat=",", title_text="Cumulative Savings", secondary_y=True)
    return fig


# ─── Deep dive ────────────────────────────────────────────────────────────────

def build_category_drilldown(category_id: int | None, months_prev: int) -> go.Figure:
    """Stacked bar of a category's descendants over the last months_prev months."""
    if category_id is None:
        fig = go.Figure()
        fig.update_layout(
            title="Select a category above to see its breakdown over time",
            height=400,
        )
        return fig

    sub_ids = cath.get_all_category_descendants(category_id)
    sub_ids.append(category_id)

    labels, _ = _month_series(months_prev)
    traces = []

    for sc_id in sub_ids:
        name = cath.category_id_to_name(sc_id)
        transactions = transr.recall_transaction_category(sc_id)
        _, mts = anah.month_bin_transaction_total(transactions, months_prev)
        # month_bin_transaction_total sums raw values; expenses are negative — flip
        mts_abs = [abs(v) for v in mts]
        if any(v > 0 for v in mts_abs):
            traces.append((sum(mts_abs), name, mts_abs))

    # Sort largest total to bottom of stack
    traces.sort(key=lambda x: x[0])

    cat_name = cath.category_id_to_name(category_id)
    fig = go.Figure()
    for _, name, mts_abs in traces:
        fig.add_trace(go.Bar(
            name=name,
            x=labels,
            y=mts_abs,
            hovertemplate=f"<b>{name}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=f"{cat_name} — subcategory breakdown, {_period_label(months_prev)}",
        yaxis=dict(tickprefix="$", tickformat=","),
        xaxis=dict(tickangle=-45),
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=80, l=60, r=160),
        height=480,
    )
    return fig


def get_transaction_rows(
    months_prev: int = 6,
    keyword: str = "",
    date_start: str | None = None,
    date_end: str | None = None,
    category_id: int | None = None,
    include_descendants: bool = False,
    account_id: int | None = None,
    amount_min: float | None = None,
    amount_max: float | None = None,
) -> list[dict]:
    """
    Multi-filter transaction search for the dashboard DataTable.

    Date logic: if both date_start and date_end are provided, they override
    months_prev. Otherwise months_prev applies (0 = all time).
    Category filter optionally expands to all descendants.
    Category and account names are resolved in bulk to keep DB round-trips low.
    """
    if date_start and date_end:
        transactions = transr.recall_transaction_data(date_start, date_end)
    else:
        transactions = _period_transactions(months_prev)

    kw = keyword.strip().lower() if keyword else ""
    if kw:
        transactions = [t for t in transactions if kw in (t.description or "").lower()]

    if category_id is not None:
        if include_descendants:
            allowed = set(cath.get_all_category_descendants(category_id))
            allowed.add(category_id)
            transactions = [t for t in transactions if t.category_id in allowed]
        else:
            transactions = [t for t in transactions if t.category_id == category_id]

    if account_id is not None:
        transactions = [t for t in transactions if t.account_id == account_id]

    if amount_min is not None:
        transactions = [t for t in transactions if t.value >= amount_min]

    if amount_max is not None:
        transactions = [t for t in transactions if t.value <= amount_max]

    # Bulk-resolve category and account names
    cat_ids  = {t.category_id for t in transactions}
    acc_ids  = {t.account_id  for t in transactions}
    cat_map  = {cid: cath.category_id_to_name(cid) for cid in cat_ids}
    acc_map  = {aid: dbh.account.get_account_name_from_id(aid) for aid in acc_ids}

    rows = []
    for t in sorted(transactions, key=lambda x: x.date, reverse=True):
        rows.append({
            "date":        t.date,
            "description": t.description or "",
            "amount":      round(t.value, 2),
            "category":    cat_map.get(t.category_id, ""),
            "account":     acc_map.get(t.account_id, ""),
            "note":        t.note or "",
        })
    return rows


def build_sankey(date_start: str | None, date_end: str | None,
                 view_mode: str = "top_level") -> go.Figure:
    """
    Spending flow Sankey for an explicit date range.
    If either date is None, falls back to all-time (no filter).
    """
    if date_start and date_end:
        transactions = transr.recall_transaction_data(date_start, date_end)
        range_label = f"{date_start} to {date_end}"
    else:
        transactions = transr.recall_transaction_data()
        range_label = "all time"

    if not transactions:
        fig = go.Figure()
        fig.update_layout(title=f"No transactions found ({range_label})")
        return fig

    if view_mode == "top_level":
        categories = cath.get_top_level_categories()
    else:
        categories = cath.load_categories()

    spending_data = anah.generate_sankey_data(transactions, categories, view_mode=view_mode)
    labels, sources, targets, values = anah.process_sankey_data(spending_data)

    view_label = "Top-Level" if view_mode == "top_level" else "Hierarchical"
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=labels,
        ),
        link=dict(source=sources, target=targets, value=values),
    ))
    fig.update_layout(
        title=f"Spending Flow — {view_label} ({range_label})",
        font_size=12,
        height=560,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


# ─── Period summary (Executive summary stats) ─────────────────────────────────

def compute_period_summary(months_prev: int) -> dict:
    """Income / expenses / delta over the selected period, skipping transfer categories.
    months_prev=0 means all time."""
    transactions = _period_transactions(months_prev)
    income, expenses = _income_expense_split(transactions)
    if months_prev and months_prev > 0:
        date_start = dateh.get_date_previous(months_prev * 30)
        date_end = dateh.get_cur_str_date()
    else:
        date_start = _earliest_transaction_date() or "—"
        date_end = dateh.get_cur_str_date()
    return {
        "income": income,
        "expenses": expenses,
        "delta": income - expenses,
        "txn_count": len(transactions),
        "date_start": date_start,
        "date_end": date_end,
    }


# ─── Largest transactions ─────────────────────────────────────────────────────

def get_largest_transaction_rows(months_prev: int, n: int) -> list[dict]:
    """
    Top N transactions by absolute value within the selected period.
    months_prev=0 means all time. Excludes BALANCE/SHARES/TRANSFER/etc.
    """
    transactions = _period_transactions(months_prev)

    transactions = grah.strip_non_graphical_transactions(transactions)
    transactions.sort(key=lambda t: abs(t.value), reverse=True)
    transactions = transactions[:n]

    cat_ids = {t.category_id for t in transactions}
    acc_ids = {t.account_id  for t in transactions}
    cat_map = {cid: cath.category_id_to_name(cid) for cid in cat_ids}
    acc_map = {aid: dbh.account.get_account_name_from_id(aid) for aid in acc_ids}

    return [{
        "date":        t.date,
        "description": t.description or "",
        "amount":      round(t.value, 2),
        "category":    cat_map.get(t.category_id, ""),
        "account":     acc_map.get(t.account_id, ""),
    } for t in transactions]


# ─── Month review ─────────────────────────────────────────────────────────────

def get_month_review_data(year: int, month: int) -> tuple[list[dict], list[dict]]:
    """Return (transaction_rows, category_summary_rows) for a single month."""
    transactions = transr.recall_transaction_month_bin(year, month)

    if not transactions:
        return [], []

    cat_ids = {t.category_id for t in transactions}
    acc_ids = {t.account_id  for t in transactions}
    cat_map = {cid: cath.category_id_to_name(cid) for cid in cat_ids}
    acc_map = {aid: dbh.account.get_account_name_from_id(aid) for aid in acc_ids}

    txn_rows = [{
        "date":        t.date,
        "description": t.description or "",
        "amount":      round(t.value, 2),
        "category":    cat_map.get(t.category_id, ""),
        "account":     acc_map.get(t.account_id, ""),
        "note":        t.note or "",
    } for t in sorted(transactions, key=lambda x: x.date)]

    # Category summary — expense categories only
    categories = cath.load_categories()
    top_cat_str, amounts = anah.create_top_category_amounts_array(transactions, categories, count_NA=False)
    top_cat_str, amounts = grah.strip_non_expense_categories(top_cat_str, amounts)
    amounts = grah.format_expenses(amounts)

    pairs = sorted(
        [(c, a) for c, a in zip(top_cat_str, amounts) if a != 0],
        key=lambda x: x[1],
        reverse=True,
    )
    cat_rows = [{"category": c, "amount": round(a, 2)} for c, a in pairs]

    return txn_rows, cat_rows


# ─── Investments ─────────────────────────────────────────────────────────────

def get_investment_position_rows(live_price: bool = False) -> list[dict]:
    """
    Active investment positions (net shares > 0 per ticker per account).
    Always uses file-cached prices if available; live_price=True re-fetches from APIs.
    """
    positions = invh.get_all_active_ticker(live_price=live_price)
    overrides = invh.get_all_manual_price_overrides()
    today = _dt.date.today()
    rows = []
    for pos in positions:
        acc_name = dbh.account.get_account_name_from_id(pos.account_id)
        shares_f = float(pos.shares)

        cur_price = round(pos.price, 2) if pos.price > 0 else None
        mkt_val   = round(shares_f * pos.price, 2) if pos.price > 0 else None

        # Gain% and CAGR use actual avg-cost basis from buy transactions
        avg_cost, first_buy = dbh.investments.get_ticker_cost_basis(pos.account_id, pos.ticker)

        gain_pct = None
        if cur_price and avg_cost > 0:
            gain_pct = round((cur_price / avg_cost - 1) * 100, 2)

        cagr = None
        if cur_price and avg_cost > 0 and first_buy:
            try:
                years = (_dt.date.fromisoformat(first_buy[:10]) - today).days / -365.25
                if years >= 0.083:  # at least 1 month
                    cagr = round(((cur_price / avg_cost) ** (1.0 / years) - 1) * 100, 2)
            except Exception:
                pass

        if pos.ticker in overrides:
            price_source = "override"
        elif pos.price == 0:
            price_source = "unknown"
        elif live_price:
            price_source = "live"
        else:
            price_source = "cached"

        rows.append({
            "account":       acc_name,
            "ticker":        pos.ticker,
            "type":          pos.type or "—",
            "shares":        round(shares_f, 4),
            "avg_cost":      round(avg_cost, 2) if avg_cost else None,
            "current_price": cur_price,
            "market_value":  mkt_val,
            "gain_pct":      gain_pct,
            "cagr":          cagr,
            "price_source":  price_source,
        })
    rows.sort(key=lambda r: (r["account"], r["ticker"]))
    return rows


VALID_ASSET_TYPES = ["EQUITY", "ETF", "MUTUALFUND", "BOND", "MONEYMARKET", "CRYPTOCURRENCY", "UNKNOWN"]


def get_ticker_type_rows() -> list[dict]:
    """
    All active holdings with their current asset type, for the type editor.
    Includes tickers not yet in ticker_metadata (shown as UNKNOWN).
    """
    positions = invh.get_all_active_ticker(live_price=False)
    seen: dict[str, str] = {}
    for pos in positions:
        t = pos.ticker
        if t not in seen:
            seen[t] = pos.type or "UNKNOWN"
    return [{"ticker": t, "asset_type": seen[t]} for t in sorted(seen)]


def get_price_override_rows() -> list[dict]:
    """Rows for the manual price override editor table."""
    overrides = invh.get_all_manual_price_overrides()
    rows = [{"ticker": t, "manual_price": p} for t, p in sorted(overrides.items())]
    return rows


def get_investment_transaction_rows(trans_types: list | None = None) -> list[dict]:
    """
    All raw investment transactions from the DB, optionally filtered by trans_type
    (e.g. ['BUY', 'SELL', 'DIV']). Returns rows sorted newest-first.
    DB schema: id, date, account_id, ticker, shares, trans_type, value, description, note, date_added
    """
    ledger_data = dbh.investments.get_investment_ledge_data()
    rows = []
    for row in ledger_data:
        sql_key, date, account_id, _cat_id, ticker, shares, trans_type, value, description, note, *_ = row
        if trans_types is not None and trans_type not in trans_types:
            continue
        shares_f = float(shares) if shares else 0.0
        value_f  = float(value)  if value  else 0.0
        strike   = round(value_f / shares_f, 2) if shares_f and shares_f != 0 else 0.0
        rows.append({
            "sql_key":      sql_key,
            "date":         date,
            "account":      dbh.account.get_account_name_from_id(account_id),
            "ticker":       ticker,
            "trans_type":   trans_type,
            "shares":       round(shares_f, 4),
            "strike_price": strike,
            "value":        round(value_f, 2),
            "note":         note or "",
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


# Maps yfinance/Finnhub quoteType strings to high-level allocation buckets.
_ALLOC_GROUP = {
    "EQUITY":         "Stocks",
    "ETF":            "Stocks",
    "MUTUALFUND":     "Stocks",
    "BOND":           "Bonds",
    "FIXEDINCOME":    "Bonds",
    "CRYPTOCURRENCY": "Crypto",
    "MONEYMARKET":    "Cash",
}
_ALLOC_COLORS = {
    "Stocks": "#2563eb",
    "Bonds":  "#f59e0b",
    "Cash":   "#6b7280",
    "Crypto": "#8b5cf6",
    "Other":  "#94a3b8",
}
# Distinct colors for per-type equity breakdown
_EQUITY_TYPE_COLORS = {
    "EQUITY":     "#2563eb",
    "ETF":        "#16a34a",
    "MUTUALFUND": "#0891b2",
}


def _no_data_fig(title: str, height: int = 380) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        height=height,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_investment_allocation_pie(positions: list[dict]) -> go.Figure:
    """
    High-level asset allocation pie: Stocks, Bonds, Cash, Crypto.
    Cash always includes savings/checking DB balances.
    Investment positions use market_value when available (cached or live prices).
    """
    buckets: dict[str, float] = {}

    # Investment positions — use market_value when available, cost basis as fallback
    using_cost_basis = False
    for row in positions:
        raw_type = (row.get("type") or "").upper()
        mv = row.get("market_value") or 0
        if mv > 0:
            value = mv
        else:
            avg_cost = row.get("avg_cost") or 0
            shares   = row.get("shares") or 0
            value = avg_cost * shares
            if value > 0:
                using_cost_basis = True
        if value <= 0:
            continue
        label = _ALLOC_GROUP.get(raw_type, "Other")
        buckets[label] = buckets.get(label, 0) + value

    # Always include savings (type=1) and checking (type=2) as Cash
    for acc_id in dbh.account.get_all_account_ids():
        if dbh.account.get_account_type(acc_id) in (1, 2):
            amount, _ = dbh.balance.get_recent_balance(acc_id, add_date=True)
            if amount and amount > 0:
                buckets["Cash"] = buckets.get("Cash", 0) + amount

    if not buckets:
        return _no_data_fig("Asset Allocation — no data available")

    labels = list(buckets.keys())
    values = [buckets[l] for l in labels]
    total = sum(values)

    inv_note = " (cost basis)" if using_cost_basis else ""

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=[_ALLOC_COLORS.get(l, "#94a3b8") for l in labels],
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
        textinfo="label+percent",
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Asset Allocation — ${total:,.0f} total{inv_note}",
        showlegend=False,
        margin=dict(t=60, b=40, l=20, r=20),
        height=380,
    )
    return fig


_EQUITY_TYPE_LABELS = {
    "EQUITY":     "Individual Stocks",
    "ETF":        "ETFs",
    "MUTUALFUND": "Mutual Funds",
}

# Qualitative palette with enough distinct colors for per-ticker charts.
_QUAL_PALETTE = [
    "#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#f4a261",
    "#6a4c93", "#06d6a0", "#f72585", "#4cc9f0", "#ffd166",
    "#118ab2", "#8338ec", "#fb5607", "#3a86ff", "#a2d729",
    "#264653", "#ef476f", "#ffbe0b", "#073b4c", "#a8dadc",
]


def build_equity_detail_pie(positions: list[dict]) -> go.Figure:
    """
    Breakdown of equity-type holdings into Individual Stocks, ETFs, and Mutual
    Funds. Uses market_value when available, cost basis (avg_cost × shares) as
    fallback — so all positions appear even before a price Refresh.
    """
    _EQUITY_TYPES = {"EQUITY", "ETF", "MUTUALFUND"}
    buckets: dict[str, float] = {}
    using_cost_basis = False

    for row in positions:
        raw_type = (row.get("type") or "").upper()
        if raw_type not in _EQUITY_TYPES:
            continue
        mv = row.get("market_value") or 0
        if mv > 0:
            value = mv
        else:
            # Fall back to cost basis so the chart always has data
            avg_cost = row.get("avg_cost") or 0
            shares   = row.get("shares") or 0
            value = avg_cost * shares
            if value > 0:
                using_cost_basis = True
        if value <= 0:
            continue
        label = _EQUITY_TYPE_LABELS[raw_type]
        buckets[label] = buckets.get(label, 0) + value

    if not buckets:
        return _no_data_fig("No equity positions available")

    labels = list(buckets.keys())
    values = [buckets[l] for l in labels]
    total  = sum(values)
    colors = [_EQUITY_TYPE_COLORS.get(
        next(k for k, v in _EQUITY_TYPE_LABELS.items() if v == l), "#94a3b8"
    ) for l in labels]

    basis_note = " (cost basis)" if using_cost_basis else ""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
        textinfo="label+percent",
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Equity Breakdown — ${total:,.0f}{basis_note}",
        showlegend=False,
        margin=dict(t=60, b=40, l=20, r=20),
        height=380,
    )
    return fig


def build_equity_ticker_pie(positions: list[dict]) -> go.Figure:
    """
    Per-ticker breakdown of equity-type holdings. Each slice is one ticker,
    colored with a distinct qualitative palette. Uses market_value when
    available, cost basis fallback otherwise.
    """
    _EQUITY_TYPES = {"EQUITY", "ETF", "MUTUALFUND"}
    ticker_vals: dict[str, float] = {}
    ticker_types: dict[str, str] = {}
    using_cost_basis = False

    for row in positions:
        raw_type = (row.get("type") or "").upper()
        if raw_type not in _EQUITY_TYPES:
            continue
        ticker = row["ticker"]
        mv = row.get("market_value") or 0
        if mv > 0:
            value = mv
        else:
            avg_cost = row.get("avg_cost") or 0
            shares   = row.get("shares") or 0
            value = avg_cost * shares
            if value > 0:
                using_cost_basis = True
        if value <= 0:
            continue
        ticker_vals[ticker]  = ticker_vals.get(ticker, 0) + value
        ticker_types[ticker] = _EQUITY_TYPE_LABELS.get(raw_type, raw_type)

    if not ticker_vals:
        return _no_data_fig("No equity positions available")

    # Sort largest to smallest for a cleaner chart
    sorted_tickers = sorted(ticker_vals, key=lambda t: ticker_vals[t], reverse=True)
    labels     = sorted_tickers
    values     = [ticker_vals[t] for t in sorted_tickers]
    type_names = [ticker_types[t] for t in sorted_tickers]
    colors     = [_QUAL_PALETTE[i % len(_QUAL_PALETTE)] for i in range(len(sorted_tickers))]
    total      = sum(values)

    basis_note = " (cost basis)" if using_cost_basis else ""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.35,
        marker_colors=colors,
        customdata=type_names,
        hovertemplate="<b>%{label}</b> (%{customdata})<br>$%{value:,.0f} (%{percent})<extra></extra>",
        textinfo="label+percent",
        textposition="outside",
        textfont_size=11,
    ))
    fig.update_layout(
        title=f"Holdings by Ticker — ${total:,.0f}{basis_note}",
        showlegend=False,
        margin=dict(t=60, b=40, l=60, r=60),
        height=460,
    )
    return fig


# ─── Wealth & balances ────────────────────────────────────────────────────────

# Buckets used by the asset allocation pie. Liabilities (credit cards) are excluded.
_ACCOUNT_TYPE_LABEL = {
    1: "Savings",
    2: "Checking",
    3: "Credit Card",
    4: "Investment",
}


def _recent_balance_with_date(account_id):
    """Latest recorded DB balance (no live price fetch). Returns (amount, date)."""
    return dbh.balance.get_recent_balance(account_id, add_date=True)


def get_wealth_breakdown_rows() -> list[dict]:
    """Per-account latest recorded balance + updated date. Sorted by amount desc."""
    rows = []
    for acc_id in dbh.account.get_all_account_ids():
        amount, date = _recent_balance_with_date(acc_id)
        rows.append({
            "account":  dbh.account.get_account_name_from_id(acc_id),
            "type":     _ACCOUNT_TYPE_LABEL.get(dbh.account.get_account_type(acc_id), "Other"),
            "balance":  round(amount or 0, 2),
            "updated":  date if date and date != 0 else "—",
        })
    rows.sort(key=lambda r: r["balance"], reverse=True)
    return rows


def build_asset_allocation_pie() -> go.Figure:
    """
    Simple asset allocation pie bucketed by account type from recorded DB balances.
    Investment accounts are further split into Retirement vs Taxable.
    No live price fetches — fast and deterministic.
    """
    retirement_ids = set(dbh.account.get_retirement_accounts(1))
    buckets: dict[str, float] = {}

    for acc_id in dbh.account.get_all_account_ids():
        amount, _ = _recent_balance_with_date(acc_id)
        amount = amount or 0
        if amount <= 0:
            continue  # skip liabilities and empty accounts for an asset pie
        acc_type = dbh.account.get_account_type(acc_id)
        if acc_type in (1, 2):
            label = "Cash"
        elif acc_type == 4:
            label = "Retirement" if acc_id in retirement_ids else "Taxable Investment"
        else:
            continue  # exclude credit cards from the asset pie
        buckets[label] = buckets.get(label, 0) + amount

    if not buckets:
        fig = go.Figure()
        fig.update_layout(title="No balance data available")
        return fig

    labels = list(buckets.keys())
    values = [buckets[l] for l in labels]
    total = sum(values)

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
        textinfo="label+percent",
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Asset allocation — recorded balances  (${total:,.0f} total)",
        showlegend=False,
        margin=dict(t=60, b=20, l=20, r=20),
        height=420,
    )
    return fig


def _binned_account_balances(days_prev: int, N: int):
    """
    Returns (edge_dates, account_ids, values_matrix) where values_matrix[i]
    is a list of N balances for account_ids[i] across the N time bins.
    Thin wrapper over anah.gen_Bx_matrix so we can stack-plot in Plotly.
    days_prev=0 resolves to the full history back to the earliest balance snapshot.
    """
    days_prev = _resolve_balance_days(days_prev)
    spl_Bx, edge_codes = anah.gen_Bx_matrix(dateh.get_cur_date(), days_prev, N)
    account_ids = list(spl_Bx[0].keys()) if spl_Bx else []
    values_matrix = [[a_A[aid] for a_A in spl_Bx] for aid in account_ids]
    return edge_codes, account_ids, values_matrix


def build_balance_by_account(days_prev: int = 560, N: int = 5,
                              account_ids_filter: list | None = None,
                              portfolio_only: bool = False) -> go.Figure:
    """
    Stacked area chart of recorded balances per account over time.
    account_ids_filter: if provided, only include these account IDs.
    portfolio_only: if True, restrict to investment accounts (type=4).
    """
    resolved_days = _resolve_balance_days(days_prev)
    edge_codes, account_ids, values_matrix = _binned_account_balances(days_prev, N)
    if not account_ids:
        fig = go.Figure()
        fig.update_layout(title="No balance data available")
        return fig

    combined = list(zip(account_ids, values_matrix))
    if portfolio_only:
        combined = [(aid, v) for aid, v in combined if dbh.account.get_account_type(aid) == 4]
    if account_ids_filter:
        aid_set = set(account_ids_filter)
        combined = [(aid, v) for aid, v in combined if aid in aid_set]

    if not combined:
        fig = go.Figure()
        fig.update_layout(title="No accounts match the selected filters")
        return fig

    # Sort by most recent value so the biggest stack-area is at bottom.
    combined = sorted(combined, key=lambda p: p[1][-1] if p[1] else 0)

    x_labels = edge_codes[1:]
    fig = go.Figure()
    for acc_id, vals in combined:
        name = dbh.account.get_account_name_from_id(acc_id)
        fig.add_trace(go.Scatter(
            name=name,
            x=x_labels,
            y=vals,
            mode="lines",
            stackgroup="balances",
            hovertemplate=f"<b>{name}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        title=f"Balances per account — {N} bins over last {resolved_days}d (since {edge_codes[0]})",
        yaxis=dict(tickprefix="$", tickformat=","),
        margin=dict(t=60, b=40, l=60, r=160),
        legend=dict(orientation="v", x=1.02, y=0.5),
        height=460,
    )
    return fig


def build_balance_by_type(days_prev: int = 560, N: int = 5) -> go.Figure:
    """Stacked area chart of recorded balances aggregated by account type."""
    resolved_days = _resolve_balance_days(days_prev)
    edge_codes, account_ids, values_matrix = _binned_account_balances(days_prev, N)
    if not account_ids:
        fig = go.Figure()
        fig.update_layout(title="No balance data available")
        return fig

    num_types = acch.get_num_acc_type()
    type_values = [[0.0] * N for _ in range(num_types)]
    for j, acc_id in enumerate(account_ids):
        acc_type = dbh.account.get_account_type(acc_id)
        if acc_type is None:
            continue
        for i in range(N):
            type_values[acc_type - 1][i] += values_matrix[j][i]

    type_names = [t.name.replace("_", " ").title() for t in acch.get_acc_type_arr()]
    x_labels = edge_codes[1:]

    fig = go.Figure()
    for i, name in enumerate(type_names):
        fig.add_trace(go.Scatter(
            name=name,
            x=x_labels,
            y=type_values[i],
            mode="lines",
            stackgroup="types",
            hovertemplate=f"<b>{name}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        title=f"Balances by account type — {N} bins over last {resolved_days}d (since {edge_codes[0]})",
        yaxis=dict(tickprefix="$", tickformat=","),
        margin=dict(t=60, b=40, l=60, r=120),
        legend=dict(orientation="v", x=1.02, y=0.5),
        height=420,
    )
    return fig


def build_single_account_balance(account_id: int | None) -> go.Figure:
    """Day-by-day modeled balance for one account (falls back to raw snapshots)."""
    if account_id is None:
        fig = go.Figure()
        fig.update_layout(title="Select an account above to see its balance over time", height=380)
        return fig

    name = dbh.account.get_account_name_from_id(account_id)
    try:
        history = balh.model_account_balance(account_id)
    except Exception:
        history = None

    if history:
        dates = [d for d, _ in history]
        bals = [b for _, b in history]
    else:
        raw = dbh.balance.get_balance_by_account_id(account_id)
        if not raw:
            fig = go.Figure()
            fig.update_layout(title=f"No balance data for {name}", height=380)
            return fig
        dates = [r[3] for r in raw]
        bals = [r[2] for r in raw]

    fig = go.Figure(go.Scatter(
        x=dates, y=bals, mode="lines",
        line=dict(color="#1a2940", width=2),
        hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=f"Balance over time — {name}",
        yaxis=dict(tickprefix="$", tickformat=","),
        margin=dict(t=60, b=40, l=60, r=20),
        height=420,
    )
    return fig


def get_balance_ledger_rows(account_id: int | None = None) -> list[dict]:
    """All recorded balance snapshots, optionally filtered to one account."""
    if account_id:
        raw = dbh.balance.get_balance_by_account_id(account_id)
    else:
        raw = dbh.balance.get_balance_ledge_data()

    return [{
        "sql_key": r[0],
        "account": dbh.account.get_account_name_from_id(r[1]),
        "balance": round(r[2], 2),
        "date":    r[3],
    } for r in raw]


# ─── Retirement Monte Carlo ───────────────────────────────────────────────────

def run_retirement_monte_carlo(
    current_age: float,
    retirement_age: float,
    death_age: float,
    annual_return_mean: float,
    annual_return_stddev: float,
    inflation_mean: float,
    inflation_stddev: float,
    num_simulations: int = 5000,
) -> dict:
    """
    Monte Carlo retirement projection. Uses real returns (return adjusted for inflation).
    Current balance is summed from accounts flagged retirement=1 in the DB.
    Returns simulation arrays + percentile summary.
    """
    working_years = max(retirement_age - current_age, 0)
    retired_years = max(death_age - retirement_age, 0.0001)

    # Pull retirement balances from DB (recorded balances — no live fetch)
    retirement_ids = dbh.account.get_retirement_accounts(1)
    current_balance = sum(
        dbh.balance.get_recent_balance(aid) or 0 for aid in retirement_ids
    )

    final_balances = []
    monthly_withdrawals = []

    working_years_int = int(working_years)
    retired_years_int = int(retired_years)

    for _ in range(num_simulations):
        returns = np.random.normal(annual_return_mean, annual_return_stddev, working_years_int)
        inflations = np.random.normal(inflation_mean, inflation_stddev, working_years_int)
        real_returns = [(1 + r) / (1 + i) - 1 for r, i in zip(returns, inflations)]

        bal = current_balance
        for rr in real_returns:
            bal *= (1 + rr)
        final_balances.append(bal)

        ret_returns = np.random.normal(annual_return_mean, annual_return_stddev, retired_years_int)
        ret_inflations = np.random.normal(inflation_mean, inflation_stddev, retired_years_int)
        ret_real = [(1 + r) / (1 + i) - 1 for r, i in zip(ret_returns, ret_inflations)]
        avg_real_ret = float(np.mean(ret_real)) if ret_real else 0.0

        r_m = avg_real_ret / 12
        if r_m != 0 and retired_years_int > 0:
            monthly = (bal * r_m) / (1 - pow(1 + r_m, -12 * retired_years_int))
        elif retired_years_int > 0:
            monthly = bal / (12 * retired_years_int)
        else:
            monthly = 0
        monthly_withdrawals.append(monthly)

    bal_pct = np.percentile(final_balances, [10, 50, 90])
    with_pct = np.percentile(monthly_withdrawals, [10, 50, 90])

    return {
        "current_balance": current_balance,
        "final_balances": final_balances,
        "monthly_withdrawals": monthly_withdrawals,
        "balance_p10": bal_pct[0],
        "balance_p50": bal_pct[1],
        "balance_p90": bal_pct[2],
        "withdraw_p10": with_pct[0],
        "withdraw_p50": with_pct[1],
        "withdraw_p90": with_pct[2],
    }


# ─── Category tree ────────────────────────────────────────────────────────────

def build_category_treemap() -> go.Figure:
    """
    Treemap of the full category hierarchy. Equal leaf sizes so the chart
    represents structure rather than spending volume — the tooltip surfaces
    each category's keyword count.
    """
    categories = cath.load_categories()
    if not categories:
        fig = go.Figure()
        fig.update_layout(title="No categories defined")
        return fig

    categories = [c for c in categories if c.id != 0]
    ids, labels, parents, values, keyword_counts = [], [], [], [], []
    id_to_name = {c.id: c.name for c in categories}

    for c in categories:
        ids.append(str(c.id))
        labels.append(c.name)
        # parent=1 in the schema means "top level"; map to empty string for treemap root
        parents.append(str(c.parent) if c.parent and c.parent != 1 else "")
        values.append(1)
        keyword_counts.append(len(c.keyword))

    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="remainder",
        textinfo="label",
        hovertemplate=(
            "<b>%{label}</b>"
            "<br>category_id: %{id}"
            "<br>parent_id: %{parent}"
            "<br>keywords: %{customdata}"
            "<extra></extra>"
        ),
        customdata=keyword_counts,
        marker=dict(line=dict(width=1, color="#fff")),
    ))
    fig.update_layout(
        title=f"Category hierarchy — {len(categories)} categories",
        margin=dict(t=60, b=20, l=20, r=20),
        height=560,
    )
    return fig


def get_category_tree_text() -> str:
    """
    Hierarchical printout of every category as an indented markdown code block.
    Format per line: '  ├── NAME  [id=X → parent=Y]  • N keywords: k1, k2, …'
    """
    categories = cath.load_categories()
    if not categories:
        return "```\n(no categories defined)\n```"

    # id=0 is a special NA placeholder; exclude it to avoid a self-referential cycle
    # (its parent_id=0 is falsy, so it would map to the virtual-root key 0 and recurse forever).
    categories = [c for c in categories if c.id != 0]
    by_id: dict[int, object] = {c.id: c for c in categories}
    children_of: dict[int, list[int]] = {}
    for c in categories:
        parent = c.parent if c.parent and c.parent != 1 else 0  # 0 = virtual root
        children_of.setdefault(parent, []).append(c.id)

    # Sort each level alphabetically
    for kids in children_of.values():
        kids.sort(key=lambda cid: by_id[cid].name)

    lines: list[str] = []

    def _walk(cid: int, prefix: str, is_last: bool, is_root_level: bool):
        c = by_id[cid]
        connector = "" if is_root_level else ("└── " if is_last else "├── ")
        kw_preview = ", ".join(c.keyword[:4])
        if len(c.keyword) > 4:
            kw_preview += f", … (+{len(c.keyword) - 4} more)"
        kw_part = f"  • {len(c.keyword)} keyword{'s' if len(c.keyword) != 1 else ''}"
        if c.keyword:
            kw_part += f": {kw_preview}"
        lines.append(f"{prefix}{connector}{c.name}  [id={c.id} → parent={c.parent}]{kw_part}")

        kids = children_of.get(cid, [])
        new_prefix = prefix + ("" if is_root_level else ("    " if is_last else "│   "))
        for i, kid in enumerate(kids):
            _walk(kid, new_prefix, i == len(kids) - 1, is_root_level=False)

    roots = children_of.get(0, [])
    lines.append(f"ROOT (parent_id=1)  — {len(roots)} top-level categor{'y' if len(roots) == 1 else 'ies'}")
    for i, rid in enumerate(roots):
        _walk(rid, "", i == len(roots) - 1, is_root_level=False)

    return "```\n" + "\n".join(lines) + "\n```"


def build_retirement_histogram(sim_result: dict) -> go.Figure:
    """Histogram of simulated retirement balances with percentile markers."""
    balances = sim_result["final_balances"]
    p10, p50, p90 = sim_result["balance_p10"], sim_result["balance_p50"], sim_result["balance_p90"]

    fig = go.Figure(go.Histogram(
        x=balances,
        nbinsx=60,
        marker_color="#4466cc",
        hovertemplate="$%{x:,.0f}<br>%{y} simulations<extra></extra>",
    ))
    for pct, label, color in [(p10, "10th %ile", "#e05252"),
                              (p50, "Median",    "#1a2940"),
                              (p90, "90th %ile", "#52a852")]:
        fig.add_vline(
            x=pct, line_dash="dash", line_color=color,
            annotation_text=f"{label}: ${pct:,.0f}",
            annotation_position="top",
        )
    fig.update_layout(
        title="Simulated retirement balance distribution",
        xaxis=dict(title="Balance at retirement (today's $)", tickprefix="$", tickformat=","),
        yaxis=dict(title="Simulations"),
        margin=dict(t=80, b=60, l=60, r=20),
        height=420,
    )
    return fig
