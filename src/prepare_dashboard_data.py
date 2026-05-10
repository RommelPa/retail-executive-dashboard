from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

DASHBOARD_TRANSACTIONS_PATH = PROCESSED_DATA_DIR / "dashboard_transactions.csv"
EXECUTIVE_KPIS_PATH = PROCESSED_DATA_DIR / "executive_kpis.csv"
MONTHLY_REVENUE_PATH = PROCESSED_DATA_DIR / "monthly_revenue.csv"
COUNTRY_SUMMARY_PATH = PROCESSED_DATA_DIR / "country_summary.csv"
PRODUCT_SUMMARY_PATH = PROCESSED_DATA_DIR / "product_summary.csv"
CUSTOMER_SUMMARY_PATH = PROCESSED_DATA_DIR / "customer_summary.csv"

EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Load raw Online Retail data.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data file not found at {path}. "
            "Place online_retail.csv inside data/raw/."
        )

    data = pd.read_csv(
        path,
        dtype={
            "InvoiceNo": "str",
            "StockCode": "str",
            "Description": "str",
            "CustomerID": "float64",
            "Country": "str",
        },
        parse_dates=["InvoiceDate"],
        low_memory=False,
    )

    return data


def validate_raw_columns(data: pd.DataFrame) -> None:
    """
    Validate raw columns before processing.
    """
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in data.columns]

    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")


def build_dashboard_transactions(raw_data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean raw retail data and create dashboard-ready transaction rows.

    v1 scope:
    - keep valid sales only,
    - exclude cancellations,
    - exclude non-positive quantities,
    - exclude non-positive prices,
    - remove exact duplicates.
    """
    data = raw_data.copy()

    initial_rows = len(data)

    duplicate_rows = data.duplicated().sum()
    data = data.drop_duplicates().copy()

    rows_after_deduplication = len(data)

    data["is_cancellation"] = data["InvoiceNo"].str.startswith("C", na=False)

    cancellation_rows = data["is_cancellation"].sum()
    non_positive_quantity_rows = (data["Quantity"] <= 0).sum()
    non_positive_price_rows = (data["UnitPrice"] <= 0).sum()

    valid_sales = data[
        (~data["is_cancellation"])
        & (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
    ].copy()

    valid_sales["Revenue"] = valid_sales["Quantity"] * valid_sales["UnitPrice"]

    valid_sales["InvoiceDate"] = pd.to_datetime(valid_sales["InvoiceDate"])
    valid_sales["InvoiceDateOnly"] = valid_sales["InvoiceDate"].dt.date
    valid_sales["Year"] = valid_sales["InvoiceDate"].dt.year
    valid_sales["Month"] = valid_sales["InvoiceDate"].dt.month
    valid_sales["YearMonth"] = valid_sales["InvoiceDate"].dt.to_period("M").astype(str)
    valid_sales["DayOfWeek"] = valid_sales["InvoiceDate"].dt.day_name()

    valid_sales["Description"] = valid_sales["Description"].fillna("Unknown product")
    valid_sales["Country"] = valid_sales["Country"].fillna("Unknown country")

    valid_sales["CustomerSegment"] = valid_sales["CustomerID"].apply(
        lambda value: "Identified customer" if pd.notna(value) else "Unknown customer"
    )

    valid_sales["CustomerIDClean"] = valid_sales["CustomerID"].apply(
        lambda value: str(int(value)) if pd.notna(value) else "Unknown"
    )

    dashboard_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "InvoiceDateOnly",
        "Year",
        "Month",
        "YearMonth",
        "DayOfWeek",
        "UnitPrice",
        "Revenue",
        "CustomerIDClean",
        "CustomerSegment",
        "Country",
    ]

    dashboard_transactions = (
        valid_sales[dashboard_columns]
        .sort_values("InvoiceDate")
        .reset_index(drop=True)
    )

    metadata = {
        "initial_rows": int(initial_rows),
        "duplicate_rows_removed": int(duplicate_rows),
        "rows_after_deduplication": int(rows_after_deduplication),
        "cancellation_rows_excluded": int(cancellation_rows),
        "non_positive_quantity_rows_excluded": int(non_positive_quantity_rows),
        "non_positive_price_rows_excluded": int(non_positive_price_rows),
        "valid_sales_rows": int(len(dashboard_transactions)),
    }

    return dashboard_transactions, metadata


def build_executive_kpis(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Build executive KPI snapshot.
    """
    total_revenue = transactions["Revenue"].sum()
    total_orders = transactions["InvoiceNo"].nunique()
    total_customers = transactions.loc[
        transactions["CustomerIDClean"] != "Unknown",
        "CustomerIDClean",
    ].nunique()
    total_countries = transactions["Country"].nunique()
    total_products = transactions["StockCode"].nunique()
    average_order_value = (
        transactions.groupby("InvoiceNo")["Revenue"].sum().mean()
    )

    unidentified_revenue = transactions.loc[
        transactions["CustomerIDClean"] == "Unknown",
        "Revenue",
    ].sum()

    unidentified_revenue_share = (
        unidentified_revenue / total_revenue if total_revenue else 0
    )

    kpis = pd.DataFrame(
        [
            {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "total_customers": total_customers,
                "total_countries": total_countries,
                "total_products": total_products,
                "average_order_value": average_order_value,
                "unidentified_revenue": unidentified_revenue,
                "unidentified_revenue_share": unidentified_revenue_share,
                "start_date": transactions["InvoiceDate"].min(),
                "end_date": transactions["InvoiceDate"].max(),
            }
        ]
    )

    return kpis


def build_monthly_revenue(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Build monthly revenue summary.
    """
    monthly_revenue = (
        transactions.groupby("YearMonth", as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            customers=("CustomerIDClean", lambda x: x[x != "Unknown"].nunique()),
            units_sold=("Quantity", "sum"),
        )
        .sort_values("YearMonth")
    )

    monthly_revenue["average_order_value"] = (
        monthly_revenue["revenue"] / monthly_revenue["orders"]
    )

    return monthly_revenue


def build_country_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Build revenue summary by country.
    """
    country_summary = (
        transactions.groupby("Country", as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            customers=("CustomerIDClean", lambda x: x[x != "Unknown"].nunique()),
            units_sold=("Quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_revenue = country_summary["revenue"].sum()
    country_summary["revenue_share"] = country_summary["revenue"] / total_revenue

    return country_summary


def build_product_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Build revenue summary by product.
    """
    product_summary = (
        transactions.groupby(["StockCode", "Description"], as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            units_sold=("Quantity", "sum"),
            orders=("InvoiceNo", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_revenue = product_summary["revenue"].sum()
    product_summary["revenue_share"] = product_summary["revenue"] / total_revenue

    return product_summary


def build_customer_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Build revenue summary by customer.

    Unknown customers are excluded from customer concentration analysis.
    """
    identified_transactions = transactions[
        transactions["CustomerIDClean"] != "Unknown"
    ].copy()

    customer_summary = (
        identified_transactions.groupby("CustomerIDClean", as_index=False)
        .agg(
            revenue=("Revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            units_sold=("Quantity", "sum"),
            countries=("Country", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    total_identified_revenue = customer_summary["revenue"].sum()
    customer_summary["revenue_share"] = (
        customer_summary["revenue"] / total_identified_revenue
    )
    customer_summary["cumulative_revenue_share"] = customer_summary[
        "revenue_share"
    ].cumsum()

    return customer_summary


def save_outputs(
    transactions: pd.DataFrame,
    kpis: pd.DataFrame,
    monthly_revenue: pd.DataFrame,
    country_summary: pd.DataFrame,
    product_summary: pd.DataFrame,
    customer_summary: pd.DataFrame,
) -> None:
    """
    Save processed dashboard datasets.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    transactions.to_csv(DASHBOARD_TRANSACTIONS_PATH, index=False)
    kpis.to_csv(EXECUTIVE_KPIS_PATH, index=False)
    monthly_revenue.to_csv(MONTHLY_REVENUE_PATH, index=False)
    country_summary.to_csv(COUNTRY_SUMMARY_PATH, index=False)
    product_summary.to_csv(PRODUCT_SUMMARY_PATH, index=False)
    customer_summary.to_csv(CUSTOMER_SUMMARY_PATH, index=False)


def print_summary(
    transactions: pd.DataFrame,
    kpis: pd.DataFrame,
    country_summary: pd.DataFrame,
    product_summary: pd.DataFrame,
    customer_summary: pd.DataFrame,
    metadata: dict,
) -> None:
    """
    Print dashboard data preparation summary.
    """
    print("=" * 80)
    print("RETAIL DASHBOARD DATA PREPARATION SUMMARY")
    print("=" * 80)

    print("\n1. Cleaning summary")
    for key, value in metadata.items():
        print(f"{key}: {value:,}")

    print("\n2. Dashboard KPI snapshot")
    print(kpis.round(4).to_string(index=False))

    print("\n3. Dashboard transaction date range")
    print(f"Start date: {transactions['InvoiceDate'].min()}")
    print(f"End date: {transactions['InvoiceDate'].max()}")

    print("\n4. Top 10 countries by revenue")
    print(
        country_summary[
            ["Country", "revenue", "orders", "customers", "revenue_share"]
        ]
        .head(10)
        .round(4)
        .to_string(index=False)
    )

    print("\n5. Top 10 products by revenue")
    print(
        product_summary[
            ["StockCode", "Description", "revenue", "units_sold", "orders"]
        ]
        .head(10)
        .round(2)
        .to_string(index=False)
    )

    print("\n6. Customer concentration")
    print(f"Identified customers: {len(customer_summary):,}")
    print(
        "Top 10 customers revenue share: "
        f"{customer_summary.head(10)['revenue_share'].sum() * 100:.2f}%"
    )
    print(
        "Top 50 customers revenue share: "
        f"{customer_summary.head(50)['revenue_share'].sum() * 100:.2f}%"
    )

    print("\n7. Files saved")
    print(f"Dashboard transactions: {DASHBOARD_TRANSACTIONS_PATH}")
    print(f"Executive KPIs: {EXECUTIVE_KPIS_PATH}")
    print(f"Monthly revenue: {MONTHLY_REVENUE_PATH}")
    print(f"Country summary: {COUNTRY_SUMMARY_PATH}")
    print(f"Product summary: {PRODUCT_SUMMARY_PATH}")
    print(f"Customer summary: {CUSTOMER_SUMMARY_PATH}")


if __name__ == "__main__":
    raw_retail_data = load_raw_data()
    validate_raw_columns(raw_retail_data)

    dashboard_transactions, cleaning_metadata = build_dashboard_transactions(
        raw_retail_data
    )

    executive_kpis = build_executive_kpis(dashboard_transactions)
    monthly_revenue = build_monthly_revenue(dashboard_transactions)
    country_summary = build_country_summary(dashboard_transactions)
    product_summary = build_product_summary(dashboard_transactions)
    customer_summary = build_customer_summary(dashboard_transactions)

    save_outputs(
        transactions=dashboard_transactions,
        kpis=executive_kpis,
        monthly_revenue=monthly_revenue,
        country_summary=country_summary,
        product_summary=product_summary,
        customer_summary=customer_summary,
    )

    print_summary(
        transactions=dashboard_transactions,
        kpis=executive_kpis,
        country_summary=country_summary,
        product_summary=product_summary,
        customer_summary=customer_summary,
        metadata=cleaning_metadata,
    )