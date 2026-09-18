"""
@file monthly_digest.py
@brief builds and renders a self-contained HTML summary of one month's financial activity --
       a lightweight "did anything look off this month" check-in, complementing (not replacing)
       the interactive dashboard.

Split into two stages on purpose: `build_digest_data()` gathers plain-dict data with no HTML
involved (independently testable, reusable elsewhere later e.g. a dashboard panel), and
`render_digest_html()` turns that dict into markup. Nothing here sends email or touches the
filesystem -- callers decide what to do with the returned string.
"""

# import needed modules
import html as _html

# import user defined modules
import db.helpers as dbh
from analysis.data_recall import transaction_recall as transr
from analysis import analyzer_helper as anah
from analysis.graphing import graphing_helper as grah
from categories import categories_helper as cath
from tools import date_helper as dateh

# Transfer/internal categories excluded from income & expense totals. Kept in sync BY HAND with
# web/charts.py's `_SKIP_CATS` -- analysis/ intentionally does not import from web/ (see CLAUDE.md
# "Architecture Notes": charts call the analysis layer, not the other way around), so this can't be
# a shared import without restructuring that layering. If you touch one, check the other.
_SKIP_CATS = {"BALANCE", "SHARES", "TRANSFER", "PAYMENT", "VALUE", "INTERNAL"}


def _income_expense_split(transactions):
    income = expenses = 0.0
    for t in transactions:
        if cath.category_id_to_name(t.category_id) in _SKIP_CATS:
            continue
        if t.value > 0:
            income += t.value
        else:
            expenses += abs(t.value)
    return income, expenses


def build_digest_data(year=None, month=None, baseline_months=6, anomaly_stddev=2.0):
    """
    Gathers every stat the digest needs for one month into a plain dict.

    If year/month are omitted, walks back from LAST month (not the current, still-in-progress
    one -- its partial totals would look like a false "spent way less than usual" anomaly in
    every category) to the most recent month that actually has transaction data. Same
    convention as charts.build_mom_comparison / exec_summary_02, so this works right after a
    normal monthly load.
    """
    if year is None or month is None:
        year, month, _ = dateh.get_date_int_array()
        year, month = dateh.get_previous_month(year, month)
        for _ in range(12):
            if transr.recall_transaction_month_bin(year, month):
                break
            year, month = dateh.get_previous_month(year, month)

    transactions = transr.recall_transaction_month_bin(year, month)

    income, expenses = _income_expense_split(transactions)
    net = income - expenses
    savings_rate = (net / income * 100) if income > 0 else 0.0

    net_worth = sum(
        dbh.balance.get_recent_balance(acc_id) or 0
        for acc_id in dbh.account.get_all_account_ids()
    )

    anomalies = anah.get_category_anomalies(
        months_prev=baseline_months, stddev_threshold=anomaly_stddev,
        target_year=year, target_month=month,
    )

    # Full top-level category breakdown for the month, sorted by spend descending -- gives
    # context beyond just the flagged anomalies (e.g. "what did I actually spend on").
    categories = cath.load_categories()
    cat_names, cat_amounts = anah.create_top_category_amounts_array(transactions, categories, count_NA=False)
    cat_names, cat_amounts = grah.strip_non_expense_categories(cat_names, cat_amounts)
    category_totals = sorted(
        (
            {"category": name, "amount": abs(amount)}
            for name, amount in zip(cat_names, cat_amounts)
            if amount != 0
        ),
        key=lambda row: -row["amount"],
    )

    return {
        "period_label": f"{year}-{month:02d}",
        "year": year,
        "month": month,
        "generated_at": dateh.get_cur_str_date(),
        "income": income,
        "expenses": expenses,
        "net": net,
        "savings_rate": savings_rate,
        "transaction_count": len(transactions),
        "net_worth": net_worth,
        "anomalies": anomalies,
        "category_totals": category_totals,
        "baseline_months": baseline_months,
        "anomaly_stddev": anomaly_stddev,
    }


##############################################################################
####      HTML RENDERING                    ##################################
##############################################################################

# Palette lifted from web/app.py so the digest reads as the same product as the dashboard.
_NAVY = "#1a2940"
_MUTED = "#6b7a90"
_GREEN = "#52a852"
_RED = "#e05252"
_CARD_BG = "#ffffff"
_PAGE_BG = "#f0f2f5"
_BORDER = "#dde2ea"


def _money(amount, show_sign=False):
    sign = "+" if (show_sign and amount > 0) else ""
    return f"{sign}${amount:,.2f}"


def _fmt_z(z_score):
    if z_score == float("inf"):
        return "new spending"
    if z_score == float("-inf"):
        return "stopped entirely"
    return f"{z_score:+.1f}σ"


def _kpi_card(label, value, color=_NAVY):
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{_html.escape(label)}</div>
      <div class="kpi-value" style="color:{color};">{value}</div>
    </div>"""


def _anomaly_rows(anomalies):
    if not anomalies:
        return '<tr><td colspan="4" class="empty-row">No categories deviated significantly from their baseline this month.</td></tr>'
    rows = []
    for a in anomalies:
        color = _RED if a["delta_abs"] > 0 else _GREEN
        rows.append(f"""
        <tr>
          <td>{_html.escape(a["category"])}</td>
          <td class="num">{_money(a["current"])}</td>
          <td class="num">{_money(a["baseline_mean"])}</td>
          <td class="num" style="color:{color}; font-weight:600;">{_fmt_z(a["z_score"])} ({a["delta_pct"]:+.0f}%)</td>
        </tr>""")
    return "".join(rows)


def _category_rows(category_totals):
    if not category_totals:
        return '<tr><td colspan="2" class="empty-row">No categorized spending found for this month.</td></tr>'
    rows = []
    for row in category_totals:
        rows.append(f"""
        <tr>
          <td>{_html.escape(row["category"])}</td>
          <td class="num">{_money(row["amount"])}</td>
        </tr>""")
    return "".join(rows)


def render_digest_html(data):
    """Renders `build_digest_data()`'s output into a self-contained HTML string."""
    net_color = _GREEN if data["net"] >= 0 else _RED

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Financial Digest -- {data["period_label"]}</title>
<style>
  body {{
    font-family: system-ui, -apple-system, sans-serif;
    background: {_PAGE_BG};
    margin: 0;
    padding: 24px 32px;
    color: {_NAVY};
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 26px; font-weight: 700; margin: 0 0 4px 0; }}
  .subtitle {{ color: {_MUTED}; font-size: 13px; margin: 0 0 24px 0; }}
  .section-header {{
    font-size: 16px; font-weight: 700; color: {_NAVY};
    margin: 28px 0 12px 0; border-bottom: 2px solid {_BORDER}; padding-bottom: 6px;
  }}
  .kpi-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .kpi-card {{
    background: {_CARD_BG}; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    padding: 14px 18px; flex: 1 1 0; min-width: 140px;
  }}
  .kpi-label {{ font-size: 11px; color: {_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; }}
  .kpi-value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: {_CARD_BG}; border-radius: 10px;
           box-shadow: 0 1px 4px rgba(0,0,0,0.10); overflow: hidden; }}
  th {{ text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
        color: {_MUTED}; padding: 10px 14px; border-bottom: 2px solid {_BORDER}; }}
  td {{ padding: 9px 14px; font-size: 14px; border-bottom: 1px solid {_BORDER}; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:nth-child(odd) td {{ background: #fafbfc; }}
  .empty-row {{ color: {_MUTED}; text-align: center; padding: 16px; font-style: italic; }}
  .footer {{ color: {_MUTED}; font-size: 12px; margin-top: 28px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Financial Digest &mdash; {data["period_label"]}</h1>
  <p class="subtitle">Generated {data["generated_at"]} &middot; {data["transaction_count"]} transactions this month</p>

  <div class="kpi-row">
    {_kpi_card("Net Worth", _money(data["net_worth"]))}
    {_kpi_card("Income", _money(data["income"]), _GREEN)}
    {_kpi_card("Expenses", _money(data["expenses"]), _RED)}
    {_kpi_card("Net (Income &minus; Expenses)", _money(data["net"], show_sign=True), net_color)}
    {_kpi_card("Savings Rate", f'{data["savings_rate"]:.1f}%', net_color)}
  </div>

  <div class="section-header">Category Anomalies (vs {data["baseline_months"]}-month baseline, &ge;{data["anomaly_stddev"]:.1f}&sigma;)</div>
  <table>
    <tr><th>Category</th><th>This Month</th><th>Baseline Avg</th><th>Signal</th></tr>
    {_anomaly_rows(data["anomalies"])}
  </table>

  <div class="section-header">Category Breakdown</div>
  <table>
    <tr><th>Category</th><th>Spent</th></tr>
    {_category_rows(data["category_totals"])}
  </table>

  <p class="footer">Financial-Analyzer monthly digest &middot; generated locally, not sent anywhere.</p>
</div>
</body>
</html>
"""
