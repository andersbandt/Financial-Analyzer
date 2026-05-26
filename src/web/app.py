"""
web/app.py — Dash layout and callbacks for the Financial Dashboard.

Figure builders live in web/charts.py. Entry point: src/dashboard.py.
"""

from dash import Dash, html, dcc, Input, Output
import categories.categories_helper as cath
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
    "fontSize": "18px",
    "fontWeight": "700",
    "color": "#1a2940",
    "margin": "28px 0 12px 0",
    "borderBottom": "2px solid #dde2ea",
    "paddingBottom": "6px",
}

KPI_NUMBER = {"fontSize": "28px", "fontWeight": "700", "color": "#1a2940", "margin": "4px 0"}
KPI_LABEL  = {"fontSize": "12px", "color": "#6b7a90", "textTransform": "uppercase", "letterSpacing": "0.05em"}
KPI_SUB    = {"fontSize": "12px", "color": "#9aa5b4", "marginTop": "2px"}

PERIOD_OPTIONS = [
    {"label": "3 months",  "value": 3},
    {"label": "6 months",  "value": 6},
    {"label": "12 months", "value": 12},
    {"label": "24 months", "value": 24},
]


def _kpi_card(card_id, label, sub=""):
    return html.Div(style={**CARD, "flex": "1 1 0", "minWidth": "160px"}, children=[
        html.Div(label, style=KPI_LABEL),
        html.Div(id=card_id, style=KPI_NUMBER),
        html.Div(sub, id=f"{card_id}-sub", style=KPI_SUB),
    ])


def _dropdown(id_, options, value, width="160px", **kwargs):
    return dcc.Dropdown(id=id_, options=options, value=value,
                        clearable=False, style={"width": width}, **kwargs)


def _graph(id_, flex="1 1 0"):
    return html.Div(style={**CARD, "flex": flex, "minWidth": "0"}, children=[dcc.Graph(id=id_)])


# ─── App factory ─────────────────────────────────────────────────────────────

def create_app() -> Dash:
    app = Dash(__name__, title="Financial Dashboard")

    # Load category options once at startup (DB is already open by this point)
    all_categories = cath.load_categories()
    category_options = sorted(
        [{"label": cat.name, "value": cat.id} for cat in all_categories],
        key=lambda o: o["label"],
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    app.layout = html.Div(style=PAGE, children=[

        # ── Header ──────────────────────────────────────────────────────────
        html.H1("Financial Dashboard", style={
            "margin": "0 0 4px 0", "fontSize": "28px", "fontWeight": "700", "color": "#1a2940",
        }),
        html.P("Personal finance overview — data from local SQLite database", style={
            "margin": "0 0 24px 0", "color": "#6b7a90", "fontSize": "14px",
        }),

        # ── Global controls ──────────────────────────────────────────────────
        html.Div(style={
            **CARD, "display": "flex", "gap": "24px", "alignItems": "center",
            "marginBottom": "20px", "flexWrap": "wrap",
        }, children=[
            html.Div([
                html.Label("Period", style={**KPI_LABEL, "marginBottom": "4px", "display": "block"}),
                _dropdown("dd-period", PERIOD_OPTIONS, 6),
            ]),
            html.Div([
                html.Label("MoM baseline", style={**KPI_LABEL, "marginBottom": "4px", "display": "block"}),
                _dropdown("dd-baseline", PERIOD_OPTIONS, 3),
            ]),
        ]),

        # ── KPI cards ────────────────────────────────────────────────────────
        html.Div(style=ROW, children=[
            _kpi_card("kpi-net-worth",    "Net Worth (recorded balances)"),
            _kpi_card("kpi-monthly-spend","This Month's Spending", sub=""),
            _kpi_card("kpi-savings-rate", "Savings Rate (period)"),
        ]),

        # ════════════════ SPENDING OVERVIEW ══════════════════════════════════
        html.Div("Spending Overview", style=SECTION_HEADER),

        html.Div(style=ROW, children=[
            _graph("chart-pie"),
            _graph("chart-monthly-bar", flex="2 1 0"),
        ]),

        html.Div(style=ROW, children=[
            _graph("chart-mom"),
        ]),

        # ════════════════ INCOME & SAVINGS ═══════════════════════════════════
        html.Div("Income & Savings", style=SECTION_HEADER),

        html.Div(style=ROW, children=[
            _graph("chart-income-expenses"),
        ]),

        # ════════════════ DEEP DIVE ═══════════════════════════════════════════
        html.Div("Deep Dive", style=SECTION_HEADER),

        # Category drill-down controls
        html.Div(style={
            **CARD, "display": "flex", "gap": "24px", "alignItems": "center",
            "marginBottom": "16px", "flexWrap": "wrap",
        }, children=[
            html.Div([
                html.Label("Category", style={**KPI_LABEL, "marginBottom": "4px", "display": "block"}),
                _dropdown("dd-category", category_options, None, width="260px",
                          placeholder="Select a category…"),
            ]),
            html.Div([
                html.Label("Months", style={**KPI_LABEL, "marginBottom": "4px", "display": "block"}),
                _dropdown("dd-drilldown-months", PERIOD_OPTIONS, 12),
            ]),
        ]),

        html.Div(style=ROW, children=[
            _graph("chart-drilldown"),
        ]),

        # Sankey controls
        html.Div(style={
            **CARD, "display": "flex", "gap": "24px", "alignItems": "center",
            "marginBottom": "16px", "marginTop": "8px", "flexWrap": "wrap",
        }, children=[
            html.Div([
                html.Label("Sankey view", style={**KPI_LABEL, "marginBottom": "6px", "display": "block"}),
                dcc.RadioItems(
                    id="radio-sankey-mode",
                    options=[
                        {"label": "  Top-level categories", "value": "top_level"},
                        {"label": "  Hierarchical (parent → child)", "value": "hierarchical"},
                    ],
                    value="top_level",
                    inputStyle={"marginRight": "6px"},
                    labelStyle={"marginRight": "20px", "fontSize": "14px"},
                ),
            ]),
        ]),

        html.Div(style=ROW, children=[
            _graph("chart-sankey"),
        ]),

    ])

    # ── Callbacks ─────────────────────────────────────────────────────────────

    @app.callback(
        Output("kpi-net-worth",    "children"),
        Output("kpi-monthly-spend","children"),
        Output("kpi-monthly-spend-sub", "children"),
        Output("kpi-savings-rate", "children"),
        Input("dd-period", "value"),
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
        Input("dd-period", "value"),
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
        Input("dd-period", "value"),
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

    @app.callback(
        Output("chart-sankey", "figure"),
        Input("dd-period",         "value"),
        Input("radio-sankey-mode", "value"),
    )
    def update_sankey(months_prev, view_mode):
        return charts.build_sankey(months_prev, view_mode)

    return app
