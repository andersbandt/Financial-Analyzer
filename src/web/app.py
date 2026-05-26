"""
web/app.py — Dash dashboard for Financial Analyzer.

Entry point: src/dashboard.py (run after db_init).
"""

from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

import categories.categories_helper as cath
from analysis import analyzer_helper as anah
from analysis.graphing import graphing_helper as grah
from analysis.data_recall import transaction_recall as transr
from tools import date_helper as dateh


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------

STRIP_CATEGORIES = ["INCOME", "INTERNAL", "INVESTMENT", "MISC FINANCE"]


def _strip_and_format(cat_names, amounts):
    """Remove non-expense categories, strip zeroes, and make amounts positive."""
    cat_names, amounts = grah.strip_non_expense_categories(cat_names, amounts)
    cat_names, amounts = grah.strip_zero_categories(cat_names, amounts)
    amounts = grah.format_expenses(amounts)
    return cat_names, amounts


def build_spending_pie(months_prev):
    date_end = dateh.get_cur_str_date()
    date_start = dateh.get_date_previous(months_prev * 30)
    transactions = transr.recall_transaction_data(date_start, date_end)

    if not transactions:
        fig = go.Figure()
        fig.update_layout(title="No transactions found for this period")
        return fig

    categories = cath.load_categories()
    cat_names, amounts = anah.create_top_category_amounts_array(transactions, categories, count_NA=False)
    cat_names, amounts = _strip_and_format(cat_names, amounts)

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


def build_monthly_bar(months_prev):
    [current_year, current_month, _] = dateh.get_date_int_array()

    oldest_month = current_month - months_prev + 1
    oldest_year = current_year
    while oldest_month < 1:
        oldest_month += 12
        oldest_year -= 1

    date_bin_trans = []
    labels = []
    year, month = oldest_year, oldest_month
    for _ in range(months_prev):
        date_bin_trans.append(transr.recall_transaction_month_bin(year, month))
        labels.append(f"{year}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1

    bin_dicts = anah.gen_bin_analysis_dict(date_bin_trans)

    if not bin_dicts or not bin_dicts[0]["categories"]:
        fig = go.Figure()
        fig.update_layout(title="No category data found")
        return fig

    cat_names = bin_dicts[0]["categories"]
    # Build {category: [amount_per_month]} — amounts flipped positive
    cat_amounts = {cat: [abs(d["amounts"][i]) for d in bin_dicts]
                   for i, cat in enumerate(cat_names)}

    # Sort categories by total descending so the legend is readable
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


def build_mom_comparison(baseline_months):
    """Bar chart: previous month spending vs N-month baseline average, shown as % delta."""
    [current_year, current_month, _] = dateh.get_date_int_array()

    # Find the most recent month that has data
    prev_year, prev_month = dateh.get_previous_month(current_year, current_month)
    for _ in range(12):
        prev_trans = transr.recall_transaction_month_bin(prev_year, prev_month)
        if prev_trans:
            break
        prev_year, prev_month = dateh.get_previous_month(prev_year, prev_month)

    if not prev_trans:
        fig = go.Figure()
        fig.update_layout(title="No recent transaction data found")
        return fig

    # Baseline: the N months before prev_month
    baseline_end_month = prev_month - 1
    baseline_end_year = prev_year
    while baseline_end_month < 1:
        baseline_end_month += 12
        baseline_end_year -= 1

    baseline_start_month = baseline_end_month - baseline_months + 1
    baseline_start_year = baseline_end_year
    while baseline_start_month < 1:
        baseline_start_month += 12
        baseline_start_year -= 1

    start_range = dateh.month_year_to_date_range(baseline_start_year, baseline_start_month)
    end_range = dateh.month_year_to_date_range(baseline_end_year, baseline_end_month)
    baseline_trans = transr.recall_transaction_data(start_range[0], end_range[1])

    categories = cath.load_categories()
    cat_names, prev_amounts = anah.create_top_category_amounts_array(prev_trans, categories, count_NA=False)
    _, baseline_amounts = anah.create_top_category_amounts_array(baseline_trans, categories, count_NA=False)

    original_names = cat_names[:]
    cat_names, prev_amounts = grah.strip_non_expense_categories(original_names, prev_amounts)
    _, baseline_amounts = grah.strip_non_expense_categories(original_names, baseline_amounts)

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
        title=f"vs {baseline_months}-month avg — {prev_year}-{prev_month:02d}  (red = over budget)",
        xaxis=dict(ticksuffix="%", zeroline=True, zerolinewidth=2, zerolinecolor="#888"),
        margin=dict(t=60, b=40, l=160, r=40),
        height=max(300, len(cat_names) * 24 + 80),
    )
    return fig


# ---------------------------------------------------------------------------
# App layout + callbacks
# ---------------------------------------------------------------------------

PERIOD_OPTIONS = [
    {"label": "3 months", "value": 3},
    {"label": "6 months", "value": 6},
    {"label": "12 months", "value": 12},
    {"label": "24 months", "value": 24},
]

CARD_STYLE = {
    "background": "#fff",
    "borderRadius": "8px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.12)",
    "padding": "8px",
    "flex": "1 1 0",
    "minWidth": "0",
}

PAGE_STYLE = {
    "fontFamily": "system-ui, sans-serif",
    "background": "#f4f6f9",
    "minHeight": "100vh",
    "padding": "24px",
}

HEADER_STYLE = {
    "margin": "0 0 20px 0",
    "fontSize": "28px",
    "fontWeight": "700",
    "color": "#1a2940",
}

CONTROLS_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "gap": "12px",
    "marginBottom": "20px",
}

ROW_STYLE = {
    "display": "flex",
    "gap": "20px",
    "marginBottom": "20px",
    "flexWrap": "wrap",
}


def create_app():
    app = Dash(__name__, title="Financial Dashboard")

    app.layout = html.Div(style=PAGE_STYLE, children=[
        html.H1("Financial Dashboard", style=HEADER_STYLE),

        # Controls
        html.Div(style=CONTROLS_STYLE, children=[
            html.Label("Period:", style={"fontWeight": "600"}),
            dcc.Dropdown(
                id="months-dropdown",
                options=PERIOD_OPTIONS,
                value=6,
                clearable=False,
                style={"width": "160px"},
            ),
            html.Label("MoM baseline:", style={"fontWeight": "600", "marginLeft": "20px"}),
            dcc.Dropdown(
                id="baseline-dropdown",
                options=PERIOD_OPTIONS,
                value=3,
                clearable=False,
                style={"width": "160px"},
            ),
        ]),

        # Row 1: pie + monthly bar
        html.Div(style=ROW_STYLE, children=[
            html.Div(style=CARD_STYLE, children=[dcc.Graph(id="spending-pie")]),
            html.Div(style={**CARD_STYLE, "flex": "2 1 0"}, children=[dcc.Graph(id="monthly-bar")]),
        ]),

        # Row 2: MoM comparison
        html.Div(style=ROW_STYLE, children=[
            html.Div(style={**CARD_STYLE, "flex": "1 1 0"}, children=[dcc.Graph(id="mom-bar")]),
        ]),
    ])

    @app.callback(
        Output("spending-pie", "figure"),
        Output("monthly-bar", "figure"),
        Input("months-dropdown", "value"),
    )
    def update_period_charts(months_prev):
        return build_spending_pie(months_prev), build_monthly_bar(months_prev)

    @app.callback(
        Output("mom-bar", "figure"),
        Input("baseline-dropdown", "value"),
    )
    def update_mom_chart(baseline_months):
        return build_mom_comparison(baseline_months)

    return app
