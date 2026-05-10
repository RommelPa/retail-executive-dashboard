from __future__ import annotations

from calendar import monthrange
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DASHBOARD_TRANSACTIONS_PATH = PROCESSED_DATA_DIR / "dashboard_transactions.csv"

OPERATIONAL_STOCK_CODES = {
    "DOT",
    "POST",
    "M",
    "BANK CHARGES",
    "C2",
    "D",
}

PRIMARY = "#00A99D"
SECONDARY = "#2F3E46"
ACCENT = "#FF5A5F"
WARNING = "#F4B942"
BACKGROUND = "#F4F6F8"
CARD = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#64748B"

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

st.set_page_config(
    page_title="Retail Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BACKGROUND};
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }}

        .block-container {{
            padding-top: 0.35rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}

        .dashboard-header {{
            background: linear-gradient(90deg, #263238 0%, #37474F 100%);
            color: white;
            border-radius: 18px;
            padding: 22px 28px;
            margin-bottom: 18px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.10);
        }}

        .dashboard-title {{
            font-size: 32px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.4px;
            color: #FFFFFF;
        }}

        .dashboard-subtitle {{
            font-size: 14px;
            margin-top: 6px;
            color: #D1D5DB;
        }}

        .period-pill {{
            display: inline-block;
            margin-top: 12px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 12px;
            color: #F9FAFB;
        }}

        .section-title {{
            font-size: 17px;
            font-weight: 800;
            color: #1F2937;
            margin: 14px 0 10px 0;
        }}

        .metric-card {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 16px 18px;
            min-height: 118px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
        }}

        .metric-label {{
            font-size: 12px;
            font-weight: 800;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: 850;
            color: #111827;
            line-height: 1.05;
        }}

        .metric-delta-positive {{
            font-size: 12px;
            color: #047857;
            font-weight: 700;
            margin-top: 9px;
        }}

        .metric-delta-negative {{
            font-size: 12px;
            color: #B91C1C;
            font-weight: 700;
            margin-top: 9px;
        }}

        .metric-delta-neutral {{
            font-size: 12px;
            color: #64748B;
            font-weight: 600;
            margin-top: 9px;
        }}

        .diagnosis-card {{
            background: #FFFFFF;
            border-left: 5px solid {PRIMARY};
            border-radius: 14px;
            padding: 14px 16px;
            min-height: 124px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
            border-top: 1px solid #E5E7EB;
            border-right: 1px solid #E5E7EB;
            border-bottom: 1px solid #E5E7EB;
        }}

        .diagnosis-title {{
            font-size: 13px;
            font-weight: 800;
            color: #1F2937;
            margin-bottom: 6px;
        }}

        .diagnosis-text {{
            font-size: 12px;
            color: #374151;
            line-height: 1.35;
        }}

        .chart-title {{
            font-size: 15px;
            font-weight: 800;
            color: #1F2937;
            margin-bottom: 2px;
        }}

        .chart-subtitle {{
            font-size: 11px;
            color: #64748B;
            margin-bottom: 8px;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 14px 18px 18px 18px;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
            overflow: visible !important;
        }}

        div[data-testid="stExpander"] {{
            background: #FFFFFF;
            border-radius: 14px;
            border: 1px solid #E5E7EB;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: #FFFFFF;
            border-radius: 999px;
            padding: 8px 18px;
            border: 1px solid #E5E7EB;
            color: #1F2937;
        }}

        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 0rem;
        }}

        div[data-testid="stToolbar"] {{
            display: none !important;
        }}

        button[kind="header"] {{
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            color: #1F2937 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            z-index: 999999 !important;
        }}

        button[kind="header"] {{
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            color: #1F2937 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Formatting helpers
# -----------------------------------------------------------------------------
def format_currency(value: float) -> str:
    return f"£{value:,.0f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value * 100:,.1f}%"


def compute_delta(current_value: float, previous_value: float | None) -> tuple[str, str]:
    if previous_value is None or previous_value == 0:
        return "No previous period", "neutral"

    delta = (current_value - previous_value) / previous_value
    delta_text = f"{delta * 100:+.1f}% vs previous period"

    if delta > 0:
        return delta_text, "positive"

    if delta < 0:
        return delta_text, "negative"

    return "0.0% vs previous period", "neutral"


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_dashboard_transactions() -> pd.DataFrame:
    if not DASHBOARD_TRANSACTIONS_PATH.exists():
        raise FileNotFoundError(
            "Processed dashboard data was not found. "
            "Run `python src/prepare_dashboard_data.py` first."
        )

    data = pd.read_csv(
        DASHBOARD_TRANSACTIONS_PATH,
        dtype={
            "InvoiceNo": "str",
            "StockCode": "str",
            "Description": "str",
            "CustomerIDClean": "str",
            "CustomerSegment": "str",
            "Country": "str",
        },
        parse_dates=["InvoiceDate"],
        low_memory=False,
    )

    data["InvoiceDateOnly"] = pd.to_datetime(data["InvoiceDateOnly"])
    data["YearMonthDate"] = pd.to_datetime(data["YearMonth"] + "-01")

    return data


# -----------------------------------------------------------------------------
# Filtering
# -----------------------------------------------------------------------------
def get_country_options(data: pd.DataFrame, country_mode: str, custom_countries: list[str]) -> list[str]:
    all_countries = sorted(data["Country"].dropna().unique())

    if country_mode == "All countries":
        return all_countries

    if country_mode == "United Kingdom only":
        return ["United Kingdom"]

    if country_mode == "Exclude United Kingdom":
        return [country for country in all_countries if country != "United Kingdom"]

    if country_mode == "Top international markets":
        return (
            data[data["Country"] != "United Kingdom"]
            .groupby("Country", as_index=False)
            .agg(revenue=("Revenue", "sum"))
            .sort_values("revenue", ascending=False)
            .head(10)["Country"]
            .tolist()
        )

    if country_mode == "Custom selection":
        return custom_countries

    return all_countries


def filter_transactions(
    data: pd.DataFrame,
    selected_date_range,
    selected_countries: list[str],
) -> pd.DataFrame:
    start_date, end_date = selected_date_range

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered = data[
        (data["InvoiceDateOnly"] >= start_date)
        & (data["InvoiceDateOnly"] <= end_date)
    ].copy()

    if selected_countries:
        filtered = filtered[filtered["Country"].isin(selected_countries)]

    return filtered


def build_previous_period_range(selected_date_range) -> tuple[pd.Timestamp, pd.Timestamp]:
    start_date, end_date = selected_date_range

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    period_days = (end_date - start_date).days + 1
    previous_end = start_date - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=period_days - 1)

    return previous_start, previous_end


# -----------------------------------------------------------------------------
# Aggregations
# -----------------------------------------------------------------------------
def build_kpis(data: pd.DataFrame) -> dict:
    total_revenue = data["Revenue"].sum()
    total_orders = data["InvoiceNo"].nunique()
    total_customers = data.loc[
        data["CustomerIDClean"] != "Unknown",
        "CustomerIDClean",
    ].nunique()
    total_units = data["Quantity"].sum()
    total_countries = data["Country"].nunique()

    average_order_value = (
        data.groupby("InvoiceNo")["Revenue"].sum().mean()
        if total_orders > 0
        else 0
    )

    unidentified_revenue = data.loc[
        data["CustomerIDClean"] == "Unknown",
        "Revenue",
    ].sum()

    unidentified_revenue_share = (
        unidentified_revenue / total_revenue
        if total_revenue > 0
        else 0
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_units": total_units,
        "total_countries": total_countries,
        "average_order_value": average_order_value,
        "unidentified_revenue": unidentified_revenue,
        "unidentified_revenue_share": unidentified_revenue_share,
    }


def build_monthly_revenue(data: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        data.groupby(["YearMonth", "YearMonthDate"], as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            units_sold=("Quantity", "sum"),
        )
        .sort_values("YearMonthDate")
    )

    monthly["average_order_value"] = monthly["revenue"] / monthly["orders"]

    return monthly


def build_country_summary(data: pd.DataFrame) -> pd.DataFrame:
    country = (
        data.groupby("Country", as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            customers=("CustomerIDClean", lambda x: x[x != "Unknown"].nunique()),
            units_sold=("Quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_revenue = country["revenue"].sum()
    country["revenue_share"] = country["revenue"] / total_revenue if total_revenue > 0 else 0
    country["revenue_label"] = country["revenue_share"].map(format_percent)

    return country


def build_product_summary(
    data: pd.DataFrame,
    exclude_operational_codes: bool,
) -> pd.DataFrame:
    product_data = data.copy()

    if exclude_operational_codes:
        product_data = product_data[
            ~product_data["StockCode"].isin(OPERATIONAL_STOCK_CODES)
        ]

    product = (
        product_data.groupby(["StockCode", "Description"], as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            units_sold=("Quantity", "sum"),
            orders=("InvoiceNo", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_revenue = product["revenue"].sum()
    product["revenue_share"] = product["revenue"] / total_revenue if total_revenue > 0 else 0
    product["product_label"] = product["StockCode"] + " — " + product["Description"].str.slice(0, 42)

    return product


def build_customer_summary(data: pd.DataFrame) -> pd.DataFrame:
    identified = data[data["CustomerIDClean"] != "Unknown"].copy()

    customer = (
        identified.groupby("CustomerIDClean", as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            units_sold=("Quantity", "sum"),
            countries=("Country", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_revenue = customer["revenue"].sum()
    customer["revenue_share"] = customer["revenue"] / total_revenue if total_revenue > 0 else 0
    customer["cumulative_revenue_share"] = customer["revenue_share"].cumsum()
    customer["rank"] = range(1, len(customer) + 1)

    return customer


# -----------------------------------------------------------------------------
# Diagnostics
# -----------------------------------------------------------------------------
def is_month_partial(date_value: pd.Timestamp, data_min: pd.Timestamp, data_max: pd.Timestamp) -> bool:
    date_value = pd.to_datetime(date_value)
    data_min = pd.to_datetime(data_min)
    data_max = pd.to_datetime(data_max)

    first_day = date_value.replace(day=1)
    last_day = date_value.replace(day=monthrange(date_value.year, date_value.month)[1])

    if date_value.year == data_min.year and date_value.month == data_min.month:
        return data_min > first_day

    if date_value.year == data_max.year and date_value.month == data_max.month:
        return data_max < last_day

    return False


def build_period_notes(selected_date_range, full_data: pd.DataFrame) -> list[str]:
    notes = []

    selected_start, selected_end = selected_date_range
    selected_start = pd.to_datetime(selected_start)
    selected_end = pd.to_datetime(selected_end)

    data_min = full_data["InvoiceDateOnly"].min()
    data_max = full_data["InvoiceDateOnly"].max()

    if is_month_partial(selected_start, data_min, data_max):
        notes.append(f"The selected start month ({selected_start:%b %Y}) is partial.")

    if is_month_partial(selected_end, data_min, data_max):
        notes.append(f"The selected end month ({selected_end:%b %Y}) is partial.")

    if is_month_partial(data_max, data_min, data_max):
        notes.append(
            "The final dataset month is partial. Do not interpret the last-month drop as a full-month decline."
        )

    return notes


def build_executive_diagnosis(
    kpis: dict,
    country_summary: pd.DataFrame,
    customer_summary: pd.DataFrame,
    product_summary_with_operational: pd.DataFrame,
    period_notes: list[str],
) -> list[tuple[str, str, str]]:
    diagnosis = []

    if not country_summary.empty:
        top_country = country_summary.iloc[0]

        if top_country["revenue_share"] >= 0.70:
            diagnosis.append(
                (
                    "Geographic concentration",
                    f"{top_country['Country']} represents {format_percent(top_country['revenue_share'])} of revenue. Global conclusions are dominated by this market.",
                    "risk",
                )
            )

    if kpis["unidentified_revenue_share"] >= 0.10:
        diagnosis.append(
            (
                "Customer visibility gap",
                f"{format_percent(kpis['unidentified_revenue_share'])} of revenue has no identified customer. Customer-level decisions have incomplete visibility.",
                "warning",
            )
        )

    if not customer_summary.empty:
        top_10_customer_share = customer_summary.head(10)["revenue_share"].sum()

        if top_10_customer_share >= 0.15:
            diagnosis.append(
                (
                    "Customer concentration",
                    f"Top 10 customers represent {format_percent(top_10_customer_share)} of identified revenue. Retention risk is concentrated.",
                    "risk",
                )
            )

    operational_total = product_summary_with_operational["revenue"].sum()

    if operational_total > 0:
        operational_revenue = product_summary_with_operational.loc[
            product_summary_with_operational["StockCode"].isin(OPERATIONAL_STOCK_CODES),
            "revenue",
        ].sum()

        operational_share = operational_revenue / operational_total

        if operational_share >= 0.02:
            diagnosis.append(
                (
                    "Operational stock codes",
                    f"{format_percent(operational_share)} of revenue comes from postage, manual charges, or operational codes. Product ranking should be reviewed with and without them.",
                    "warning",
                )
            )

    for note in period_notes:
        diagnosis.append(("Period coverage", note, "info"))

    if not diagnosis:
        diagnosis.append(
            (
                "No major concentration alerts",
                "The selected view does not trigger the current executive risk thresholds.",
                "info",
            )
        )

    return diagnosis[:6]


# -----------------------------------------------------------------------------
# Charts
# -----------------------------------------------------------------------------
def apply_chart_layout(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=36, r=72, t=56, b=78),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI", color="#1F2937", size=12),
        title=dict(
            font=dict(size=15, color="#111827")
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(color="#374151", size=11),
        ),
        xaxis=dict(
            tickfont=dict(color="#374151", size=11),
            title=dict(font=dict(color="#374151"), standoff=14),
            gridcolor="#E5E7EB",
            zerolinecolor="#E5E7EB",
            automargin=True,
        ),
        yaxis=dict(
            tickfont=dict(color="#374151", size=11),
            title=dict(font=dict(color="#374151"), standoff=14),
            gridcolor="#E5E7EB",
            zerolinecolor="#E5E7EB",
            automargin=True,
        ),
    )

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)

    return fig


def render_chart_card(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="chart-title">{title}</div>
        <div class="chart-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def revenue_trend_chart(monthly_revenue: pd.DataFrame) -> go.Figure:
    fig = px.line(
        monthly_revenue,
        x="YearMonthDate",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend",
        labels={"YearMonthDate": "Month", "revenue": "Revenue"},
    )
    fig.update_traces(line=dict(color=PRIMARY, width=3), marker=dict(size=8))
    fig.update_layout(yaxis_tickprefix="£", hovermode="x unified")
    return apply_chart_layout(fig, height=380)


def country_share_chart(country_summary: pd.DataFrame, top_n: int) -> go.Figure:
    donut_n = min(5, top_n)

    top_country = country_summary.head(donut_n).copy()
    other_revenue = country_summary.iloc[donut_n:]["revenue"].sum()

    if other_revenue > 0:
        top_country = pd.concat(
            [
                top_country,
                pd.DataFrame(
                    [
                        {
                            "Country": "Other",
                            "revenue": other_revenue,
                            "revenue_share": other_revenue / country_summary["revenue"].sum(),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    fig = px.pie(
        top_country,
        names="Country",
        values="revenue",
        hole=0.58,
        title="Revenue Share by Country",
        color_discrete_sequence=[
            PRIMARY,
            ACCENT,
            WARNING,
            "#577590",
            "#43AA8B",
            "#ADB5BD",
        ],
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(color="white", size=12),
        marker=dict(line=dict(color="white", width=2)),
        hovertemplate="<b>%{label}</b><br>Revenue: £%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color="#374151"),
        ),
    )

    return apply_chart_layout(fig, height=380)


def product_bar_chart(product_summary: pd.DataFrame, top_n: int) -> go.Figure:
    top_products = product_summary.head(top_n).sort_values("revenue")

    fig = px.bar(
        top_products,
        x="revenue",
        y="product_label",
        orientation="h",
        title=f"Top {top_n} Products by Revenue",
        labels={"revenue": "Revenue", "product_label": ""},
    )

    max_revenue = top_products["revenue"].max()

    fig.update_traces(
        marker_color=PRIMARY,
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_tickprefix="£",
        yaxis=dict(automargin=True),
    )

    fig.update_xaxes(range=[0, max_revenue * 1.12])

    return apply_chart_layout(fig, height=380)


def customer_concentration_chart(customer_summary: pd.DataFrame) -> go.Figure:
    concentration = customer_summary.head(100).copy()

    fig = px.area(
        concentration,
        x="rank",
        y="cumulative_revenue_share",
        title="Cumulative Revenue Share by Customer Rank",
        labels={
            "rank": "Customer Rank",
            "cumulative_revenue_share": "Cumulative Revenue Share",
        },
    )

    fig.update_traces(
        line_color=ACCENT,
        fillcolor="rgba(255, 107, 107, 0.25)",
    )

    fig.update_layout(yaxis_tickformat=".0%")
    fig.update_xaxes(range=[1, 105])
    fig.update_yaxes(range=[0, min(1, concentration["cumulative_revenue_share"].max() * 1.12)])

    return apply_chart_layout(fig, height=360)


def country_bar_chart(country_summary: pd.DataFrame, top_n: int) -> go.Figure:
    top_country = country_summary.head(top_n).sort_values("revenue")

    fig = px.bar(
        top_country,
        x="revenue",
        y="Country",
        orientation="h",
        title=f"Top {top_n} Countries by Revenue",
        labels={"revenue": "Revenue", "Country": "Country"},
        text="revenue_label",
    )

    max_revenue = top_country["revenue"].max()

    fig.update_traces(
        marker_color=SECONDARY,
        textposition="outside",
        textfont=dict(color="#1F2937", size=11),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_tickprefix="£",
        yaxis=dict(categoryorder="total ascending"),
    )

    fig.update_xaxes(range=[0, max_revenue * 1.18])

    return apply_chart_layout(fig, height=360)


# -----------------------------------------------------------------------------
# UI components
# -----------------------------------------------------------------------------
def render_header(selected_date_range, country_mode: str) -> None:
    start_date, end_date = selected_date_range

    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="dashboard-title">Retail Executive Dashboard</div>
            <div class="dashboard-subtitle">
                Business performance monitoring for validated retail sales, customer concentration,
                country exposure, and product revenue.
            </div>
            <div class="period-pill">
                Period: {pd.to_datetime(start_date):%Y-%m-%d} to {pd.to_datetime(end_date):%Y-%m-%d}
                &nbsp;•&nbsp; Country view: {country_mode}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, delta_text: str, delta_status: str) -> None:
    delta_class = {
        "positive": "metric-delta-positive",
        "negative": "metric-delta-negative",
        "neutral": "metric-delta-neutral",
    }[delta_status]

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="{delta_class}">{delta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnosis_card(title: str, message: str, status: str) -> None:
    border_color = {
        "risk": ACCENT,
        "warning": WARNING,
        "info": PRIMARY,
    }.get(status, PRIMARY)

    st.markdown(
        f"""
        <div class="diagnosis-card" style="border-left-color:{border_color};">
            <div class="diagnosis-title">{title}</div>
            <div class="diagnosis-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(data: pd.DataFrame):
    st.sidebar.markdown("## Dashboard Controls")

    min_date = data["InvoiceDateOnly"].min().date()
    max_date = data["InvoiceDateOnly"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(selected_date_range) != 2:
        st.sidebar.warning("Select a start and end date.")
        st.stop()

    country_mode = st.sidebar.radio(
        "Country view",
        options=[
            "All countries",
            "United Kingdom only",
            "Exclude United Kingdom",
            "Top international markets",
            "Custom selection",
        ],
        index=0,
    )

    custom_countries = []

    if country_mode == "Custom selection":
        countries = sorted(data["Country"].dropna().unique())
        custom_countries = st.sidebar.multiselect(
            "Select countries",
            options=countries,
            default=["United Kingdom"] if "United Kingdom" in countries else [],
        )

    selected_countries = get_country_options(
        data=data,
        country_mode=country_mode,
        custom_countries=custom_countries,
    )

    exclude_operational_codes = st.sidebar.checkbox(
        "Exclude operational stock codes from product ranking",
        value=True,
        help=(
            "Excludes codes such as DOT, POST, M, BANK CHARGES, C2, and D from "
            "the product ranking only. KPIs still use total valid sales."
        ),
    )

    top_n_products = st.sidebar.slider(
        "Top products",
        min_value=5,
        max_value=25,
        value=10,
        step=5,
    )

    top_n_countries = st.sidebar.slider(
        "Top countries",
        min_value=5,
        max_value=25,
        value=10,
        step=5,
    )

    st.sidebar.divider()
    st.sidebar.caption(f"Selected countries: {len(selected_countries)}")
    st.sidebar.caption("Data layer: valid sales only")

    return (
        selected_date_range,
        country_mode,
        selected_countries,
        exclude_operational_codes,
        top_n_products,
        top_n_countries,
    )


def render_kpi_grid(kpis: dict, previous_kpis: dict | None) -> None:
    st.markdown('<div class="section-title">Executive KPI Snapshot</div>', unsafe_allow_html=True)

    metrics = [
        ("Revenue", format_currency(kpis["total_revenue"]), "total_revenue"),
        ("Orders", format_number(kpis["total_orders"]), "total_orders"),
        ("Customers", format_number(kpis["total_customers"]), "total_customers"),
        ("Avg. Order Value", format_currency(kpis["average_order_value"]), "average_order_value"),
        ("Units Sold", format_number(kpis["total_units"]), "total_units"),
        ("Countries", format_number(kpis["total_countries"]), "total_countries"),
        ("Unidentified Revenue", format_currency(kpis["unidentified_revenue"]), "unidentified_revenue"),
        ("Unidentified Share", format_percent(kpis["unidentified_revenue_share"]), "unidentified_revenue_share"),
    ]

    row1 = st.columns(4)
    row2 = st.columns(4)

    for index, (label, value, key) in enumerate(metrics):
        previous_value = previous_kpis[key] if previous_kpis else None
        delta_text, delta_status = compute_delta(kpis[key], previous_value)

        target_column = row1[index] if index < 4 else row2[index - 4]

        with target_column:
            render_metric_card(label, value, delta_text, delta_status)


def render_executive_diagnosis(diagnosis: list[tuple[str, str, str]]) -> None:
    st.markdown('<div class="section-title">Executive Diagnosis</div>', unsafe_allow_html=True)

    columns = st.columns(3)

    for index, (title, message, status) in enumerate(diagnosis):
        with columns[index % 3]:
            render_diagnosis_card(title, message, status)


def render_tables(
    country_summary: pd.DataFrame,
    product_summary: pd.DataFrame,
    customer_summary: pd.DataFrame,
) -> None:
    with st.expander("Detailed Tables"):
        tab1, tab2, tab3 = st.tabs(["Countries", "Products", "Customers"])

        with tab1:
            table = country_summary[
                ["Country", "revenue", "orders", "customers", "units_sold", "revenue_share"]
            ].copy()

            table["revenue"] = table["revenue"].map(format_currency)
            table["revenue_share"] = table["revenue_share"].map(format_percent)

            st.dataframe(table, width="stretch", hide_index=True)

        with tab2:
            table = product_summary[
                ["StockCode", "Description", "revenue", "units_sold", "orders", "revenue_share"]
            ].copy()

            table["revenue"] = table["revenue"].map(format_currency)
            table["revenue_share"] = table["revenue_share"].map(format_percent)

            st.dataframe(table.head(50), width="stretch", hide_index=True)

        with tab3:
            table = customer_summary[
                [
                    "CustomerIDClean",
                    "revenue",
                    "orders",
                    "units_sold",
                    "countries",
                    "revenue_share",
                    "cumulative_revenue_share",
                ]
            ].copy()

            table["revenue"] = table["revenue"].map(format_currency)
            table["revenue_share"] = table["revenue_share"].map(format_percent)
            table["cumulative_revenue_share"] = table["cumulative_revenue_share"].map(format_percent)

            st.dataframe(table.head(50), width="stretch", hide_index=True)


def render_data_notes() -> None:
    with st.expander("Data Scope and Assumptions"):
        st.markdown(
            """
            **Scope**

            This dashboard uses valid sales transactions only.

            Excluded from the dashboard data layer:

            - cancelled invoices,
            - non-positive quantities,
            - non-positive unit prices,
            - exact duplicate rows.

            **Important interpretation notes**

            - Revenue is calculated as `Quantity × UnitPrice`.
            - Customer concentration excludes unidentified customers.
            - Product rankings may include operational stock codes unless the sidebar option excludes them.
            - The first and last dataset months may be partial.
            - The dashboard is designed for executive monitoring, not accounting reconciliation.
            """
        )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    inject_css()

    try:
        transactions = load_dashboard_transactions()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    (
        selected_date_range,
        country_mode,
        selected_countries,
        exclude_operational_codes,
        top_n_products,
        top_n_countries,
    ) = render_sidebar(transactions)

    render_header(selected_date_range, country_mode)

    filtered_transactions = filter_transactions(
        data=transactions,
        selected_date_range=selected_date_range,
        selected_countries=selected_countries,
    )

    if filtered_transactions.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    previous_start, previous_end = build_previous_period_range(selected_date_range)

    previous_transactions = filter_transactions(
        data=transactions,
        selected_date_range=(previous_start, previous_end),
        selected_countries=selected_countries,
    )

    kpis = build_kpis(filtered_transactions)
    previous_kpis = build_kpis(previous_transactions) if not previous_transactions.empty else None

    monthly_revenue = build_monthly_revenue(filtered_transactions)
    country_summary = build_country_summary(filtered_transactions)

    product_summary = build_product_summary(
        data=filtered_transactions,
        exclude_operational_codes=exclude_operational_codes,
    )

    product_summary_with_operational = build_product_summary(
        data=filtered_transactions,
        exclude_operational_codes=False,
    )

    customer_summary = build_customer_summary(filtered_transactions)

    period_notes = build_period_notes(
        selected_date_range=selected_date_range,
        full_data=transactions,
    )

    diagnosis = build_executive_diagnosis(
        kpis=kpis,
        country_summary=country_summary,
        customer_summary=customer_summary,
        product_summary_with_operational=product_summary_with_operational,
        period_notes=period_notes,
    )

    render_kpi_grid(kpis, previous_kpis=previous_kpis)
    render_executive_diagnosis(diagnosis)

    st.markdown('<div class="section-title">Performance Overview</div>', unsafe_allow_html=True)

    top_row_left, top_row_right = st.columns([1.35, 1])

    with top_row_left:
        with st.container(border=False):
            render_chart_card(
                "Revenue Trend",
                "Monthly valid sales revenue for the selected filters.",
            )
            st.plotly_chart(
                revenue_trend_chart(monthly_revenue),
                width="stretch",
                config=PLOTLY_CONFIG,
            )

    with top_row_right:
        render_chart_card(
            "Country Mix",
            "Revenue concentration by country.",
        )
        st.plotly_chart(
            country_share_chart(country_summary, top_n=top_n_countries),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

    bottom_row_left, bottom_row_right = st.columns(2)

    with bottom_row_left:
        render_chart_card(
            "Product Ranking",
            "Top revenue products. Operational codes can be excluded from the sidebar.",
        )
        st.plotly_chart(
            product_bar_chart(product_summary, top_n=top_n_products),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

    with bottom_row_right:
        render_chart_card(
            "Customer Concentration",
            "Cumulative revenue concentration across identified customers.",
        )
        st.plotly_chart(
            customer_concentration_chart(customer_summary),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

    st.markdown('<div class="section-title">Country Detail</div>', unsafe_allow_html=True)
    st.plotly_chart(
        country_bar_chart(country_summary, top_n=top_n_countries),
        width="stretch",
        config=PLOTLY_CONFIG,
    )

    col1, col2 = st.columns(2)

    top_10_customer_share = customer_summary.head(10)["revenue_share"].sum() if not customer_summary.empty else 0
    top_50_customer_share = customer_summary.head(50)["revenue_share"].sum() if not customer_summary.empty else 0

    with col1:
        render_metric_card(
            "Top 10 Customer Revenue Share",
            format_percent(top_10_customer_share),
            "Identified customers only",
            "neutral",
        )

    with col2:
        render_metric_card(
            "Top 50 Customer Revenue Share",
            format_percent(top_50_customer_share),
            "Identified customers only",
            "neutral",
        )

    render_tables(
        country_summary=country_summary,
        product_summary=product_summary,
        customer_summary=customer_summary,
    )

    render_data_notes()


if __name__ == "__main__":
    main()