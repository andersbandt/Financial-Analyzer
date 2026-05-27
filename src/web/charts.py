"""
web/charts.py — Plotly figure builders for the Financial Dashboard.

Each build_* function returns a go.Figure. compute_kpis() returns a plain
dict of scalar values for the KPI card row.
"""

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import db.helpers as dbh
import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis.graphing import graphing_helper as grah
from analysis.data_recall import transaction_recall as transr
from tools import date_helper as dateh

# Categories whose transactions should be excluded from income/expense charts.
# These are accounting transfers, not real cashflow.
_SKIP_CATS = {"BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"}

# Simple per-session cache so repeated chart builds don't hammer the DB.
_cat_name_cache: dict[int, str] = {}


def _cat_name(cat_id: int) -> str:
    if cat_id not in _cat_name_cache:
        _cat_name_cache[cat_id] = cath.category_id_to_name(cat_id)
    return _cat_name_cache[cat_id]


def _month_series(months_prev: int):
    """Return (labels, [(year, month), ...]) for the last months_prev months."""
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
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    transactions = transr.recall_transaction_data(date_start, date_end)

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
        title=f"Spending breakdown — last {months_prev} months  (${total:,.0f} total)",
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
        title=f"Monthly spending — last {months_prev} months",
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

    # Savings rate over the selected period
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    period_trans = transr.recall_transaction_data(date_start, date_end)
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
        title=f"Income vs Expenses — last {months_prev} months",
        xaxis=dict(tickangle=-45),
        margin=dict(t=60, b=80, l=60, r=60),
        height=500,
        legend=dict(orientation="h", x=0, y=1.08),
    )
    fig.update_yaxes(tickprefix="$", tickformat=",", secondary_y=False)
    fig.update_yaxes(ticksuffix="%", title_text="Savings Rate", secondary_y=True)
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
        title=f"{cat_name} — subcategory breakdown, last {months_prev} months",
        yaxis=dict(tickprefix="$", tickformat=","),
        xaxis=dict(tickangle=-45),
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(t=60, b=80, l=60, r=160),
        height=480,
    )
    return fig


def get_transaction_rows(months_prev: int, keyword: str = "") -> list[dict]:
    """
    Return a list of row dicts for the transaction DataTable.

    Filters by the last months_prev months. If keyword is non-empty, further
    filters to rows whose description contains the keyword (case-insensitive).
    Category and account names are resolved in bulk to keep DB round-trips low.
    """
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    transactions = transr.recall_transaction_data(date_start, date_end)

    kw = keyword.strip().lower()
    if kw:
        transactions = [t for t in transactions if kw in (t.description or "").lower()]

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


def build_sankey(months_prev: int, view_mode: str = "top_level") -> go.Figure:
    """Spending flow Sankey diagram."""
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    transactions = transr.recall_transaction_data(date_start, date_end)

    if not transactions:
        fig = go.Figure()
        fig.update_layout(title="No transactions found for this period")
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
        title=f"Spending Flow — {view_label} ({date_start} to {date_end})",
        font_size=12,
        height=560,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig
