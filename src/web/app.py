"""
web/app.py — Dash layout and callbacks for the Financial Dashboard.

Figure builders live in web/charts.py. Entry point: src/dashboard.py.

Layout is a tabbed interface (Overview / Spending / Income & Savings /
Balances / Retirement / Transactions). The Period dropdown above the tabs
drives most charts; some tabs have their own local controls.
"""

from dash import Dash, html, dcc, Input, Output, State, dash_table
import plotly.graph_objects as go

import categories.categories_helper as cath
import db.helpers as dbh
from tools import date_helper as dateh
from web import charts


# ─── Style constants ──────────────────────────────────────────────────────────

PAGE = {
    "fontFamily": "system-ui, -apple-system, sans-serif",
    "background": "#f0f2f5",
    "minHeight": "100vh",
    "padding": "24px 32px",
}

CARD = {
    "background": "#fff",
    "borderRadius": "10px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.10)",
    "padding": "16px",
}

ROW = {"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"}

SECTION_HEADER = {
    "fontSize": "16px",
    "fontWeight": "700",
    "color": "#1a2940",
    "margin": "20px 0 12px 0",
    "borderBottom": "2px solid #dde2ea",
    "paddingBottom": "6px",
}

KPI_NUMBER = {"fontSize": "28px", "fontWeight": "700", "color": "#1a2940", "margin": "4px 0"}
KPI_LABEL  = {"fontSize": "12px", "color": "#6b7a90", "textTransform": "uppercase", "letterSpacing": "0.05em"}
KPI_SUB    = {"fontSize": "12px", "color": "#9aa5b4", "marginTop": "2px"}

# Unified period dropdown options. Value is months; 0 = sentinel for "all time".
# Used everywhere a period selector appears so the UX is consistent.
PERIOD_OPTIONS = [
    {"label": "3 months",  "value": 3},
    {"label": "6 months",  "value": 6},
    {"label": "12 months", "value": 12},
    {"label": "24 months", "value": 24},
    {"label": "5 years",   "value": 60},
    {"label": "All time",  "value": 0},
]

# Balance chart uses day units (gen_Bx_matrix needs days). 0 = "all time".
BALANCE_DAYS_OPTIONS = [
    {"label": "180 days", "value": 180},
    {"label": "1 year",   "value": 365},
    {"label": "2 years",  "value": 730},
    {"label": "5 years",  "value": 1825},
    {"label": "All time", "value": 0},
]

# ─── Tab styling ──────────────────────────────────────────────────────────────

TABS_PARENT_STYLE = {
    "background": "#fff",
    "borderRadius": "10px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.10)",
    "marginBottom": "20px",
    "padding": "0 12px",
    "borderBottom": "1px solid #e4e8ee",
}
TAB_STYLE = {
    "padding": "14px 22px",
    "fontWeight": "600",
    "fontSize": "14px",
    "border": "none",
    "borderBottom": "3px solid transparent",
    "backgroundColor": "transparent",
    "color": "#6b7a90",
}
TAB_SELECTED_STYLE = {
    **TAB_STYLE,
    "borderBottom": "3px solid #1a2940",
    "color": "#1a2940",
    "backgroundColor": "transparent",
}
TAB_CONTENT_STYLE = {"paddingTop": "8px"}

# Shared DataTable styling so the new tables match the existing transaction table.
_TABLE_STYLE = dict(
    sort_action="native",
    filter_action="native",
    page_action="native",
    page_size=15,
    style_table={"overflowX": "auto"},
    style_header={
        "backgroundColor": "#f0f2f5",
        "fontWeight": "700",
        "fontSize": "12px",
        "textTransform": "uppercase",
        "letterSpacing": "0.04em",
        "border": "none",
        "borderBottom": "2px solid #dde2ea",
    },
    style_cell={
        "fontSize": "13px",
        "padding": "8px 12px",
        "border": "none",
        "borderBottom": "1px solid #f0f2f5",
        "textAlign": "left",
        "maxWidth": "320px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    },
)

# Amount columns get tabular-num right-aligned + red/green for negative/positive.
_AMOUNT_CELL_CONDITIONAL = [
    {"if": {"column_id": "amount"},  "textAlign": "right", "fontVariantNumeric": "tabular-nums"},
    {"if": {"column_id": "balance"}, "textAlign": "right", "fontVariantNumeric": "tabular-nums"},
]
_AMOUNT_DATA_CONDITIONAL = [
    {"if": {"filter_query": "{amount} < 0"}, "color": "#c0392b"},
    {"if": {"filter_query": "{amount} > 0"}, "color": "#27ae60"},
    {"if": {"row_index": "odd"},  "backgroundColor": "#fafbfc"},
]


# ─── Small component helpers ──────────────────────────────────────────────────

def _kpi_card(card_id, label, sub=""):
    return html.Div(style={**CARD, "flex": "1 1 0", "minWidth": "160px"}, children=[
        html.Div(label, style=KPI_LABEL),
        html.Div(id=card_id, style=KPI_NUMBER),
        html.Div(sub, id=f"{card_id}-sub", style=KPI_SUB),
    ])


def _dropdown(id_, options, value, width="160px", clearable=False, **kwargs):
    return dcc.Dropdown(id=id_, options=options, value=value,
                        clearable=clearable, style={"width": width}, **kwargs)


def _graph(id_, flex="1 1 0"):
    return html.Div(style={**CARD, "flex": flex, "minWidth": "0"}, children=[dcc.Graph(id=id_)])


def _control_bar(*children):
    """Card-wrapped horizontal row of controls (label + input pairs)."""
    return html.Div(style={
        **CARD, "display": "flex", "gap": "24px", "alignItems": "center",
        "marginBottom": "16px", "flexWrap": "wrap",
    }, children=list(children))


def _labeled(label_text, control):
    return html.Div([
        html.Label(label_text, style={**KPI_LABEL, "marginBottom": "4px", "display": "block"}),
        control,
    ])


# ─── Tab content builders ─────────────────────────────────────────────────────

def _overview_tab():
    return html.Div(style=TAB_CONTENT_STYLE, children=[
        _control_bar(
            _labeled("Period", _dropdown("dd-overview-period", PERIOD_OPTIONS, 6, width="180px")),
        ),
        html.Div(style=ROW, children=[
            _kpi_card("kpi-net-worth",    "Net Worth (recorded balances)"),
            _kpi_card("kpi-monthly-spend","This Month's Spending", sub=""),
            _kpi_card("kpi-savings-rate", "Savings Rate (period)"),
        ]),
        html.Div(style=ROW, children=[
            _kpi_card("kpi-period-income",   "Income (period)"),
            _kpi_card("kpi-period-expenses", "Expenses (period)"),
            _kpi_card("kpi-period-delta",    "Net Δ (income − expenses)"),
            _kpi_card("kpi-period-txns",     "Transaction Count"),
        ]),
        html.Div(style=ROW, children=[
            _graph("chart-pie"),
            _graph("chart-monthly-bar", flex="2 1 0"),
        ]),
    ])


def _spending_tab(category_options):
    # Sankey defaults to the last 12 months
    sankey_end = dateh.get_cur_str_date()
    sankey_start = dateh.get_date_previous(365)

    return html.Div(style=TAB_CONTENT_STYLE, children=[
        # Month-over-month vs baseline
        html.Div("Month-over-month vs baseline average", style=SECTION_HEADER),
        _control_bar(
            _labeled("Baseline window", _dropdown("dd-baseline", PERIOD_OPTIONS, 6)),
        ),
        html.Div(style=ROW, children=[_graph("chart-mom")]),

        # Category drill-down
        html.Div("Category drill-down", style=SECTION_HEADER),
        _control_bar(
            _labeled("Category", _dropdown("dd-category", category_options, None, width="260px",
                                           placeholder="Select a category…")),
            _labeled("Window", _dropdown("dd-drilldown-months", PERIOD_OPTIONS, 12)),
        ),
        html.Div(style=ROW, children=[_graph("chart-drilldown")]),

        # Sankey — with explicit date range
        html.Div("Spending flow (Sankey)", style=SECTION_HEADER),
        _control_bar(
            _labeled("Date range",
                dcc.DatePickerRange(
                    id="sankey-date-range",
                    start_date=sankey_start,
                    end_date=sankey_end,
                    display_format="YYYY-MM-DD",
                    style={"fontSize": "13px"},
                )),
            _labeled("Quick set", _dropdown("dd-sankey-quickset", [
                {"label": "— pick —", "value": "none"},
                {"label": "Last 3 months",  "value": "3m"},
                {"label": "Last 6 months",  "value": "6m"},
                {"label": "Last 12 months", "value": "12m"},
                {"label": "Last 24 months", "value": "24m"},
                {"label": "Last 5 years",   "value": "5y"},
                {"label": "Year to date",   "value": "ytd"},
                {"label": "All time",       "value": "all"},
            ], "none", width="180px")),
            html.Div([
                html.Label("View", style={**KPI_LABEL, "marginBottom": "6px", "display": "block"}),
                dcc.RadioItems(
                    id="radio-sankey-mode",
                    options=[
                        {"label": "  Top-level", "value": "top_level"},
                        {"label": "  Hierarchical", "value": "hierarchical"},
                    ],
                    value="top_level",
                    inputStyle={"marginRight": "6px"},
                    labelStyle={"marginRight": "16px", "fontSize": "14px"},
                ),
            ]),
        ),
        html.Div(style=ROW, children=[_graph("chart-sankey")]),
    ])


def _income_tab():
    return html.Div(style=TAB_CONTENT_STYLE, children=[
        _control_bar(
            _labeled("Period", _dropdown("dd-income-period", PERIOD_OPTIONS, 12, width="180px")),
        ),
        html.Div(style=ROW, children=[_graph("chart-income-expenses")]),
    ])


def _wealth_tab(account_options):
    return html.Div(style=TAB_CONTENT_STYLE, children=[
        # Asset allocation + wealth breakdown
        html.Div("Asset allocation & current balances", style=SECTION_HEADER),
        html.Div(style=ROW, children=[
            _graph("chart-asset-allocation"),
            html.Div(style={**CARD, "flex": "1 1 0", "minWidth": "0"}, children=[
                html.Div("Wealth Breakdown", style={**KPI_LABEL, "marginBottom": "8px"}),
                dash_table.DataTable(
                    id="wealth-table",
                    columns=[
                        {"name": "Account",  "id": "account", "type": "text"},
                        {"name": "Type",     "id": "type",    "type": "text"},
                        {"name": "Balance",  "id": "balance", "type": "numeric",
                         "format": {"specifier": ",.2f"}},
                        {"name": "Updated",  "id": "updated", "type": "text"},
                    ],
                    data=[],
                    style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfc"},
                    ],
                    **_TABLE_STYLE,
                ),
            ]),
        ]),

        # Balance over time
        html.Div("Balances over time", style=SECTION_HEADER),
        _control_bar(
            _labeled("Look back", _dropdown("dd-balance-days", BALANCE_DAYS_OPTIONS, 365)),
            _labeled("Bins (snapshots)", _dropdown("dd-balance-bins", [
                {"label": "5",  "value": 5},
                {"label": "8",  "value": 8},
                {"label": "12", "value": 12},
            ], 5)),
        ),
        html.Div(style=ROW, children=[_graph("chart-balance-by-account")]),
        html.Div(style=ROW, children=[_graph("chart-balance-by-type")]),

        # Single account
        html.Div("Single account — day-by-day modeled balance", style=SECTION_HEADER),
        _control_bar(
            _labeled("Account", _dropdown("dd-single-account", account_options, None, width="280px",
                                          placeholder="Select an account…")),
        ),
        html.Div(style=ROW, children=[_graph("chart-single-account")]),

        # Balance ledger
        html.Div("Recorded balance snapshots", style=SECTION_HEADER),
        html.Div(style=CARD, children=[
            dash_table.DataTable(
                id="balance-ledger-table",
                columns=[
                    {"name": "SQL Key", "id": "sql_key", "type": "numeric"},
                    {"name": "Account", "id": "account", "type": "text"},
                    {"name": "Balance", "id": "balance", "type": "numeric",
                     "format": {"specifier": ",.2f"}},
                    {"name": "Date",    "id": "date",    "type": "text"},
                ],
                data=[],
                style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfc"},
                ],
                **_TABLE_STYLE,
            ),
        ]),
    ])


def _retirement_tab():
    num_input_style = {
        "width": "120px", "padding": "6px 10px", "borderRadius": "6px",
        "border": "1px solid #cdd5df", "fontSize": "14px",
        "fontVariantNumeric": "tabular-nums",
    }
    def _num_input(id_, value, min_, max_, step):
        return dcc.Input(id=id_, type="number", value=value,
                         min=min_, max=max_, step=step, debounce=True,
                         style=num_input_style)

    return html.Div(style=TAB_CONTENT_STYLE, children=[
        html.Div(style={**CARD, "marginBottom": "16px"}, children=[
            html.Div(style={"display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                            "gap": "20px"}, children=[
                _labeled("Current age",          _num_input("rm-current-age",    30, 18, 100, 1)),
                _labeled("Retirement age",       _num_input("rm-retire-age",     60, 30, 100, 1)),
                _labeled("Death age",            _num_input("rm-death-age",      95, 40, 120, 1)),
                _labeled("Annual return mean (%)",   _num_input("rm-return-mean",    6,  -10, 30, 0.1)),
                _labeled("Return stddev (%)",        _num_input("rm-return-std",     2,  0,   30, 0.1)),
                _labeled("Inflation mean (%)",       _num_input("rm-inflation-mean", 3,  -5,  20, 0.1)),
                _labeled("Inflation stddev (%)",     _num_input("rm-inflation-std",  1,  0,   20, 0.1)),
                _labeled("Simulations", _dropdown("rm-num-sims", [
                    {"label": "1,000",  "value": 1000},
                    {"label": "5,000",  "value": 5000},
                    {"label": "10,000", "value": 10000},
                ], 5000)),
            ]),
            html.Div(style={"marginTop": "16px"}, children=[
                html.Button("Run simulation", id="rm-run", n_clicks=0, style={
                    "padding": "8px 20px", "fontSize": "14px", "fontWeight": "600",
                    "background": "#1a2940", "color": "#fff", "border": "none",
                    "borderRadius": "6px", "cursor": "pointer",
                }),
                html.Span(id="rm-status", style={"marginLeft": "16px", "color": "#6b7a90", "fontSize": "13px"}),
            ]),
        ]),
        html.Div(style=ROW, children=[
            _kpi_card("rm-current-balance",   "Retirement Balance (today)"),
            _kpi_card("rm-balance-p50",       "Projected Balance (median)"),
            _kpi_card("rm-withdraw-p50",      "Monthly Withdrawal (median)"),
        ]),
        html.Div(style=ROW, children=[_graph("chart-retirement-hist")]),
    ])


def _categories_tab():
    return html.Div(style=TAB_CONTENT_STYLE, children=[
        html.Div("Category hierarchy (treemap)", style=SECTION_HEADER),
        html.P("Each tile is a category; nested tiles are children. "
               "Hover for the id → parent_id mapping and keyword count.",
               style={"color": "#6b7a90", "fontSize": "13px", "margin": "0 0 12px 0"}),
        html.Div(style=ROW, children=[_graph("chart-category-treemap")]),

        html.Div("Full tree printout", style=SECTION_HEADER),
        html.P("Indented hierarchy of every category with its database id, parent_id, and keyword list. "
               "Useful as a printable reference.",
               style={"color": "#6b7a90", "fontSize": "13px", "margin": "0 0 12px 0"}),
        html.Div(style={**CARD, "marginBottom": "16px"}, children=[
            dcc.Markdown(
                id="category-tree-text",
                children="",
                style={
                    "fontSize": "13px",
                    "fontFamily": "Menlo, Consolas, monospace",
                    "whiteSpace": "pre",
                    "overflowX": "auto",
                },
            ),
        ]),
    ])


def _transactions_tab(year_options, cur_year, cur_month, category_options, account_options):
    text_input_style = {
        "width": "100%", "padding": "6px 10px", "borderRadius": "6px",
        "border": "1px solid #cdd5df", "fontSize": "14px",
    }
    num_input_style = {
        "width": "120px", "padding": "6px 10px", "borderRadius": "6px",
        "border": "1px solid #cdd5df", "fontSize": "14px",
        "fontVariantNumeric": "tabular-nums",
    }

    return html.Div(style=TAB_CONTENT_STYLE, children=[
        # Transaction search — multi-filter
        html.Div("Search transactions", style=SECTION_HEADER),
        html.Div(style={**CARD, "marginBottom": "16px"}, children=[
            html.Div(style={"display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                            "gap": "16px"}, children=[
                _labeled("Description keyword",
                    dcc.Input(id="txn-keyword", type="text",
                              placeholder="e.g. amazon, starbucks…",
                              debounce=True, style=text_input_style)),
                _labeled("Period (overridden by date range below)",
                    _dropdown("dd-txn-period", PERIOD_OPTIONS, 6, width="100%")),
                _labeled("Specific date range",
                    dcc.DatePickerRange(
                        id="txn-date-range",
                        start_date=None, end_date=None,
                        display_format="YYYY-MM-DD",
                        clearable=True,
                        style={"fontSize": "13px"},
                    )),
                _labeled("Category",
                    _dropdown("txn-category", category_options, None, width="100%",
                              placeholder="Any category…",
                              clearable=True)),
                _labeled("Include subcategories",
                    dcc.Checklist(
                        id="txn-include-descendants",
                        options=[{"label": "  Match descendants of the selected category", "value": "yes"}],
                        value=[],
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"fontSize": "13px"},
                    )),
                _labeled("Account",
                    _dropdown("txn-account", account_options, None, width="100%",
                              placeholder="Any account…",
                              clearable=True)),
                _labeled("Amount min ($)",
                    dcc.Input(id="txn-amount-min", type="number", debounce=True,
                              placeholder="-9999", style=num_input_style)),
                _labeled("Amount max ($)",
                    dcc.Input(id="txn-amount-max", type="number", debounce=True,
                              placeholder="9999", style=num_input_style)),
            ]),
            html.Div(id="txn-count", style={
                "marginTop": "12px", "color": "#6b7a90", "fontSize": "13px",
            }),
        ]),
        html.Div(style=CARD, children=[
            dash_table.DataTable(
                id="txn-table",
                columns=[
                    {"name": "Date",        "id": "date",        "type": "text"},
                    {"name": "Description", "id": "description", "type": "text"},
                    {"name": "Amount ($)",  "id": "amount",      "type": "numeric",
                     "format": {"specifier": ",.2f"}},
                    {"name": "Category",    "id": "category",    "type": "text"},
                    {"name": "Account",     "id": "account",     "type": "text"},
                    {"name": "Note",        "id": "note",        "type": "text"},
                ],
                data=[],
                style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                style_data_conditional=_AMOUNT_DATA_CONDITIONAL,
                **{**_TABLE_STYLE, "page_size": 30},
            ),
        ]),

        # Largest transactions
        html.Div("Largest transactions", style=SECTION_HEADER),
        _control_bar(
            _labeled("Top N", _dropdown("dd-largest-n", [
                {"label": "10",  "value": 10},
                {"label": "25",  "value": 25},
                {"label": "50",  "value": 50},
                {"label": "100", "value": 100},
            ], 25)),
            _labeled("Window", _dropdown("dd-largest-months", PERIOD_OPTIONS, 12)),
        ),
        html.Div(style=CARD, children=[
            dash_table.DataTable(
                id="largest-table",
                columns=[
                    {"name": "Date",        "id": "date",        "type": "text"},
                    {"name": "Description", "id": "description", "type": "text"},
                    {"name": "Amount ($)",  "id": "amount",      "type": "numeric",
                     "format": {"specifier": ",.2f"}},
                    {"name": "Category",    "id": "category",    "type": "text"},
                    {"name": "Account",     "id": "account",     "type": "text"},
                ],
                data=[],
                style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                style_data_conditional=_AMOUNT_DATA_CONDITIONAL,
                **_TABLE_STYLE,
            ),
        ]),

        # Month review
        html.Div("Month review", style=SECTION_HEADER),
        _control_bar(
            _labeled("Year",  _dropdown("dd-review-year",  year_options, cur_year, width="120px")),
            _labeled("Month", _dropdown("dd-review-month",
                [{"label": f"{m:02d}", "value": m} for m in range(1, 13)],
                cur_month, width="100px")),
            html.Div(id="review-count", style={"color": "#6b7a90", "fontSize": "13px", "alignSelf": "flex-end"}),
        ),
        html.Div(style=ROW, children=[
            html.Div(style={**CARD, "flex": "1 1 0", "minWidth": "0"}, children=[
                html.Div("Category Summary", style={**KPI_LABEL, "marginBottom": "8px"}),
                dash_table.DataTable(
                    id="review-category-table",
                    columns=[
                        {"name": "Category", "id": "category", "type": "text"},
                        {"name": "Amount",   "id": "amount",   "type": "numeric",
                         "format": {"specifier": ",.2f"}},
                    ],
                    data=[],
                    style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfc"},
                    ],
                    **{**_TABLE_STYLE, "page_size": 20},
                ),
            ]),
            html.Div(style={**CARD, "flex": "2 1 0", "minWidth": "0"}, children=[
                html.Div("Transactions", style={**KPI_LABEL, "marginBottom": "8px"}),
                dash_table.DataTable(
                    id="review-txn-table",
                    columns=[
                        {"name": "Date",        "id": "date",        "type": "text"},
                        {"name": "Description", "id": "description", "type": "text"},
                        {"name": "Amount ($)",  "id": "amount",      "type": "numeric",
                         "format": {"specifier": ",.2f"}},
                        {"name": "Category",    "id": "category",    "type": "text"},
                        {"name": "Account",     "id": "account",     "type": "text"},
                    ],
                    data=[],
                    style_cell_conditional=_AMOUNT_CELL_CONDITIONAL,
                    style_data_conditional=_AMOUNT_DATA_CONDITIONAL,
                    **_TABLE_STYLE,
                ),
            ]),
        ]),
    ])


# ─── App factory ─────────────────────────────────────────────────────────────

def create_app() -> Dash:
    app = Dash(__name__, title="Financial Dashboard")

    # Load category options once at startup (DB is already open by this point)
    all_categories = cath.load_categories()
    category_options = sorted(
        [{"label": cat.name, "value": cat.id} for cat in all_categories],
        key=lambda o: o["label"],
    )

    # Account options for the per-account balance chart
    account_options = sorted(
        [{"label": dbh.account.get_account_name_from_id(aid), "value": aid}
         for aid in dbh.account.get_all_account_ids()],
        key=lambda o: o["label"],
    )

    # Year dropdown for month review — current year and 6 prior years
    cur_year, cur_month, _ = dateh.get_date_int_array()
    year_options = [{"label": str(y), "value": y} for y in range(cur_year, cur_year - 7, -1)]

    # ── Layout ────────────────────────────────────────────────────────────────
    app.layout = html.Div(style=PAGE, children=[

        html.H1("Financial Dashboard", style={
            "margin": "0 0 4px 0", "fontSize": "28px", "fontWeight": "700", "color": "#1a2940",
        }),
        html.P("Personal finance overview — data from local SQLite database. "
               "Each tab has its own period/date controls.", style={
            "margin": "0 0 24px 0", "color": "#6b7a90", "fontSize": "14px",
        }),

        # ── Tabs ──────────────────────────────────────────────────────────────
        dcc.Tabs(
            id="main-tabs", value="overview",
            parent_style=TABS_PARENT_STYLE,
            children=[
                dcc.Tab(label="Overview", value="overview",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_overview_tab()]),
                dcc.Tab(label="Spending", value="spending",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_spending_tab(category_options)]),
                dcc.Tab(label="Income & Savings", value="income",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_income_tab()]),
                dcc.Tab(label="Balances", value="balances",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_wealth_tab(account_options)]),
                dcc.Tab(label="Retirement", value="retirement",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_retirement_tab()]),
                dcc.Tab(label="Categories", value="categories",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_categories_tab()]),
                dcc.Tab(label="Transactions", value="transactions",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[_transactions_tab(year_options, cur_year, cur_month,
                                                    category_options, account_options)]),
            ],
        ),

    ])

    # ── Callbacks ─────────────────────────────────────────────────────────────

    @app.callback(
        Output("kpi-net-worth",    "children"),
        Output("kpi-monthly-spend","children"),
        Output("kpi-monthly-spend-sub", "children"),
        Output("kpi-savings-rate", "children"),
        Input("dd-overview-period", "value"),
    )
    def update_kpis(months_prev):
        kpis = charts.compute_kpis(months_prev)
        return (
            f"${kpis['net_worth']:,.0f}",
            f"${kpis['monthly_spend']:,.0f}",
            kpis["period_label"],
            f"{kpis['savings_rate']:.1f}%",
        )

    @app.callback(
        Output("chart-pie",        "figure"),
        Output("chart-monthly-bar","figure"),
        Input("dd-overview-period", "value"),
    )
    def update_spending_charts(months_prev):
        return charts.build_spending_pie(months_prev), charts.build_monthly_bar(months_prev)

    @app.callback(
        Output("chart-mom", "figure"),
        Input("dd-baseline", "value"),
    )
    def update_mom(baseline_months):
        return charts.build_mom_comparison(baseline_months)

    @app.callback(
        Output("chart-income-expenses", "figure"),
        Input("dd-income-period", "value"),
    )
    def update_income_expenses(months_prev):
        return charts.build_income_vs_expenses(months_prev)

    @app.callback(
        Output("chart-drilldown", "figure"),
        Input("dd-category",       "value"),
        Input("dd-drilldown-months","value"),
    )
    def update_drilldown(category_id, months_prev):
        return charts.build_category_drilldown(category_id, months_prev)

    # ── Sankey: quick-period selector updates the date pickers ───────────────
    @app.callback(
        Output("sankey-date-range", "start_date"),
        Output("sankey-date-range", "end_date"),
        Input("dd-sankey-quickset", "value"),
        State("sankey-date-range", "start_date"),
        State("sankey-date-range", "end_date"),
    )
    def sankey_quickset(quickset, cur_start, cur_end):
        if not quickset or quickset == "none":
            return cur_start, cur_end
        end = dateh.get_cur_str_date()
        if quickset == "all":
            earliest = charts._earliest_transaction_date() or end
            return earliest, end
        if quickset == "ytd":
            yr, _, _ = dateh.get_date_int_array()
            return f"{yr}-01-01", end
        days_map = {"3m": 90, "6m": 180, "12m": 365, "24m": 730, "5y": 1825}
        return dateh.get_date_previous(days_map[quickset]), end

    @app.callback(
        Output("chart-sankey", "figure"),
        Input("sankey-date-range", "start_date"),
        Input("sankey-date-range", "end_date"),
        Input("radio-sankey-mode", "value"),
    )
    def update_sankey(date_start, date_end, view_mode):
        return charts.build_sankey(date_start, date_end, view_mode)

    # ── Transaction multi-filter search ──────────────────────────────────────
    @app.callback(
        Output("txn-table", "data"),
        Output("txn-count", "children"),
        Input("dd-txn-period",       "value"),
        Input("txn-keyword",         "value"),
        Input("txn-date-range",      "start_date"),
        Input("txn-date-range",      "end_date"),
        Input("txn-category",        "value"),
        Input("txn-include-descendants", "value"),
        Input("txn-account",         "value"),
        Input("txn-amount-min",      "value"),
        Input("txn-amount-max",      "value"),
    )
    def update_txn_table(months_prev, keyword, date_start, date_end,
                         category_id, include_descendants_list, account_id,
                         amount_min, amount_max):
        include_descendants = bool(include_descendants_list and "yes" in include_descendants_list)
        rows = charts.get_transaction_rows(
            months_prev=months_prev,
            keyword=keyword or "",
            date_start=date_start,
            date_end=date_end,
            category_id=category_id,
            include_descendants=include_descendants,
            account_id=account_id,
            amount_min=amount_min,
            amount_max=amount_max,
        )
        active = []
        if keyword: active.append(f"keyword '{keyword}'")
        if date_start and date_end: active.append(f"dates {date_start}→{date_end}")
        elif months_prev == 0: active.append("all time")
        else: active.append(f"last {months_prev}mo")
        if category_id is not None:
            active.append(f"category={cath.category_id_to_name(category_id)}"
                          + (" (+children)" if include_descendants else ""))
        if account_id is not None:
            active.append(f"account={dbh.account.get_account_name_from_id(account_id)}")
        if amount_min is not None: active.append(f"min ${amount_min}")
        if amount_max is not None: active.append(f"max ${amount_max}")
        count_label = (f"{len(rows):,} transaction{'s' if len(rows) != 1 else ''}"
                       f"  ·  filters: {' · '.join(active) if active else '(none)'}")
        return rows, count_label

    # ── Period summary KPIs (income / expenses / delta / count) ──────────────
    @app.callback(
        Output("kpi-period-income",   "children"),
        Output("kpi-period-expenses", "children"),
        Output("kpi-period-delta",    "children"),
        Output("kpi-period-txns",     "children"),
        Output("kpi-period-income-sub",   "children"),
        Output("kpi-period-expenses-sub", "children"),
        Output("kpi-period-delta-sub",    "children"),
        Input("dd-overview-period", "value"),
    )
    def update_period_summary(months_prev):
        s = charts.compute_period_summary(months_prev)
        rng = f"{s['date_start']} → {s['date_end']}"
        return (
            f"${s['income']:,.0f}",
            f"${s['expenses']:,.0f}",
            f"${s['delta']:,.0f}",
            f"{s['txn_count']:,}",
            rng, rng, rng,
        )

    # ── Asset allocation + wealth breakdown ──────────────────────────────────
    # No period dependency; trigger off the tabs (any selection re-renders, including initial).
    @app.callback(
        Output("chart-asset-allocation", "figure"),
        Output("wealth-table",           "data"),
        Input("main-tabs", "value"),
    )
    def update_wealth(_tab):
        return charts.build_asset_allocation_pie(), charts.get_wealth_breakdown_rows()

    # ── Categories tab — treemap + indented text printout ────────────────────
    @app.callback(
        Output("chart-category-treemap", "figure"),
        Output("category-tree-text",     "children"),
        Input("main-tabs", "value"),
    )
    def update_categories(_tab):
        return charts.build_category_treemap(), charts.get_category_tree_text()

    # ── Balance over time (by account + by type) ─────────────────────────────
    @app.callback(
        Output("chart-balance-by-account", "figure"),
        Output("chart-balance-by-type",    "figure"),
        Input("dd-balance-days", "value"),
        Input("dd-balance-bins", "value"),
    )
    def update_balance_over_time(days_prev, bins):
        return (
            charts.build_balance_by_account(days_prev, bins),
            charts.build_balance_by_type(days_prev, bins),
        )

    # ── Single account balance ───────────────────────────────────────────────
    @app.callback(
        Output("chart-single-account", "figure"),
        Input("dd-single-account", "value"),
    )
    def update_single_account(account_id):
        return charts.build_single_account_balance(account_id)

    # ── Balance ledger table ─────────────────────────────────────────────────
    @app.callback(
        Output("balance-ledger-table", "data"),
        Input("dd-single-account", "value"),  # share account selector
    )
    def update_balance_ledger(account_id):
        return charts.get_balance_ledger_rows(account_id)

    # ── Retirement Monte Carlo ───────────────────────────────────────────────
    @app.callback(
        Output("rm-current-balance", "children"),
        Output("rm-balance-p50",     "children"),
        Output("rm-withdraw-p50",    "children"),
        Output("rm-current-balance-sub", "children"),
        Output("rm-balance-p50-sub",     "children"),
        Output("rm-withdraw-p50-sub",    "children"),
        Output("chart-retirement-hist",  "figure"),
        Output("rm-status",              "children"),
        Input("rm-run", "n_clicks"),
        State("rm-current-age",     "value"),
        State("rm-retire-age",      "value"),
        State("rm-death-age",       "value"),
        State("rm-return-mean",     "value"),
        State("rm-return-std",      "value"),
        State("rm-inflation-mean",  "value"),
        State("rm-inflation-std",   "value"),
        State("rm-num-sims",        "value"),
    )
    def update_retirement(n_clicks, cur_age, ret_age, death_age,
                          ret_mean, ret_std, inf_mean, inf_std, num_sims):
        # Pull current retirement balance even before first run so the "today" KPI is populated
        if not n_clicks:
            ret_ids = dbh.account.get_retirement_accounts(1)
            cur_bal = sum(dbh.balance.get_recent_balance(aid) or 0 for aid in ret_ids)
            placeholder = go.Figure()
            placeholder.update_layout(
                title="Press 'Run simulation' to project outcomes",
                height=420, margin=dict(t=80, b=60, l=60, r=20),
            )
            return (
                f"${cur_bal:,.0f}", "—", "—",
                "from retirement-flagged accounts", "", "",
                placeholder,
                "Configure parameters above and run.",
            )

        s = charts.run_retirement_monte_carlo(
            current_age=cur_age,
            retirement_age=ret_age,
            death_age=death_age,
            annual_return_mean=ret_mean / 100,
            annual_return_stddev=ret_std / 100,
            inflation_mean=inf_mean / 100,
            inflation_stddev=inf_std / 100,
            num_simulations=int(num_sims),
        )
        fig = charts.build_retirement_histogram(s)
        return (
            f"${s['current_balance']:,.0f}",
            f"${s['balance_p50']:,.0f}",
            f"${s['withdraw_p50']:,.0f}",
            "from retirement-flagged accounts",
            f"10th: ${s['balance_p10']:,.0f}  |  90th: ${s['balance_p90']:,.0f}",
            f"10th: ${s['withdraw_p10']:,.0f}  |  90th: ${s['withdraw_p90']:,.0f}",
            fig,
            f"Ran {int(num_sims):,} simulations ({ret_age - cur_age:.0f} working yrs, {death_age - ret_age:.0f} retired yrs)",
        )

    # ── Largest transactions ─────────────────────────────────────────────────
    @app.callback(
        Output("largest-table", "data"),
        Input("dd-largest-n",      "value"),
        Input("dd-largest-months", "value"),
    )
    def update_largest(n, months_prev):
        return charts.get_largest_transaction_rows(months_prev, n)

    # ── Month review ─────────────────────────────────────────────────────────
    @app.callback(
        Output("review-txn-table",      "data"),
        Output("review-category-table", "data"),
        Output("review-count",          "children"),
        Input("dd-review-year",  "value"),
        Input("dd-review-month", "value"),
    )
    def update_month_review(year, month):
        if year is None or month is None:
            return [], [], ""
        txn_rows, cat_rows = charts.get_month_review_data(year, month)
        label = f"{len(txn_rows):,} transaction{'s' if len(txn_rows) != 1 else ''} in {year}-{month:02d}"
        return txn_rows, cat_rows, label

    return app
