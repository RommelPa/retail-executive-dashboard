from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEMO_DIR = PROJECT_ROOT / "data" / "demo"

TRANSACTIONS_PATH = PROCESSED_DIR / "dashboard_transactions.csv"

DEMO_TRANSACTIONS_PATH = DEMO_DIR / "dashboard_transactions.csv"
DEMO_KPIS_PATH = DEMO_DIR / "executive_kpis.csv"
DEMO_MONTHLY_REVENUE_PATH = DEMO_DIR / "monthly_revenue.csv"
DEMO_COUNTRY_SUMMARY_PATH = DEMO_DIR / "country_summary.csv"
DEMO_PRODUCT_SUMMARY_PATH = DEMO_DIR / "product_summary.csv"
DEMO_CUSTOMER_SUMMARY_PATH = DEMO_DIR / "customer_summary.csv"

RANDOM_STATE = 42
SAMPLE_FRACTION = 0.04
MIN_ROWS_PER_MONTH_COUNTRY = 10
MAX_ROWS_PER_MONTH_COUNTRY = 250


def load_transactions() -> pd.DataFrame:

    data = pd.read_csv(
        TRANSACTIONS_PATH,
        dtype={
            "InvoiceNo": "str",
            "StockCode": "str",
            "Description": "str",
            "Country": "str",
        },
        low_memory=False,
    )

    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")

    if "revenue" not in data.columns:
        data["revenue"] = data["Quantity"] * data["UnitPrice"]

    if "CustomerIDClean" not in data.columns:
        if "CustomerID" in data.columns:
            data["CustomerIDClean"] = data["CustomerID"].fillna("Unidentified").astype(str)
        else:
            data["CustomerIDClean"] = "Unidentified"

    return data


def create_demo_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Create a compact demo transaction layer.

    Sampling is done by month and country to preserve time and geographic coverage.
    This avoids groupby.apply behavior differences across pandas versions.
    """
    data = transactions.copy()
    data["month_key"] = data["InvoiceDate"].dt.to_period("M").astype(str)

    sampled_groups = []

    for _, group in data.groupby(["month_key", "Country"], dropna=False):
        target_rows = int(len(group) * SAMPLE_FRACTION)
        target_rows = max(MIN_ROWS_PER_MONTH_COUNTRY, target_rows)
        target_rows = min(MAX_ROWS_PER_MONTH_COUNTRY, target_rows)
        target_rows = min(len(group), target_rows)

        sampled_group = group.sample(
            n=target_rows,
            random_state=RANDOM_STATE,
        )

        sampled_groups.append(sampled_group)

    if not sampled_groups:
        raise ValueError("No demo rows were generated from processed transactions.")

    demo = pd.concat(sampled_groups, ignore_index=True)

    if "month_key" in demo.columns:
        demo = demo.drop(columns=["month_key"])

    demo = demo.sort_values("InvoiceDate").reset_index(drop=True)

    required_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerIDClean",
        "Country",
        "revenue",
    ]

    missing_columns = [
        column for column in required_columns if column not in demo.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Demo transactions are missing required columns: {missing_columns}"
        )

    return demo

def calculate_kpis(transactions: pd.DataFrame) -> pd.DataFrame:
    total_revenue = transactions["revenue"].sum()
    total_orders = transactions["InvoiceNo"].nunique()
    identified_customers = transactions.loc[
        transactions["CustomerIDClean"].ne("Unidentified"),
        "CustomerIDClean",
    ].nunique()

    unidentified_revenue = transactions.loc[
        transactions["CustomerIDClean"].eq("Unidentified"),
        "revenue",
    ].sum()

    kpis = pd.DataFrame(
        [
            {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "total_customers": identified_customers,
                "total_countries": transactions["Country"].nunique(),
                "total_products": transactions["StockCode"].nunique(),
                "average_order_value": total_revenue / total_orders if total_orders else 0,
                "unidentified_revenue": unidentified_revenue,
                "unidentified_revenue_share": (
                    unidentified_revenue / total_revenue if total_revenue else 0
                ),
                "start_date": transactions["InvoiceDate"].min(),
                "end_date": transactions["InvoiceDate"].max(),
            }
        ]
    )

    return kpis


def calculate_monthly_revenue(transactions: pd.DataFrame) -> pd.DataFrame:
    data = transactions.copy()
    data["month"] = data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        data.groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            customers=("CustomerIDClean", lambda value: value[value.ne("Unidentified")].nunique()),
            units_sold=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("month")
    )

    total_revenue = monthly["revenue"].sum()
    monthly["revenue_share"] = monthly["revenue"] / total_revenue if total_revenue else 0

    return monthly


def calculate_country_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    country = (
        transactions.groupby("Country")
        .agg(
            revenue=("revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            customers=("CustomerIDClean", lambda value: value[value.ne("Unidentified")].nunique()),
            units_sold=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    total_revenue = country["revenue"].sum()
    country["revenue_share"] = country["revenue"] / total_revenue if total_revenue else 0

    return country


def calculate_product_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    product = (
        transactions.groupby(["StockCode", "Description"])
        .agg(
            revenue=("revenue", "sum"),
            units_sold=("Quantity", "sum"),
            orders=("InvoiceNo", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    total_revenue = product["revenue"].sum()
    product["revenue_share"] = product["revenue"] / total_revenue if total_revenue else 0

    return product


def calculate_customer_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    identified = transactions[transactions["CustomerIDClean"].ne("Unidentified")].copy()

    customer = (
        identified.groupby("CustomerIDClean")
        .agg(
            revenue=("revenue", "sum"),
            orders=("InvoiceNo", "nunique"),
            units_sold=("Quantity", "sum"),
            countries=("Country", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    total_revenue = customer["revenue"].sum()
    customer["revenue_share"] = customer["revenue"] / total_revenue if total_revenue else 0
    customer["cumulative_revenue_share"] = customer["revenue_share"].cumsum()
    customer["rank"] = range(1, len(customer) + 1)

    return customer


def save_demo_data(demo_transactions: pd.DataFrame) -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    demo_transactions.to_csv(DEMO_TRANSACTIONS_PATH, index=False)
    calculate_kpis(demo_transactions).to_csv(DEMO_KPIS_PATH, index=False)
    calculate_monthly_revenue(demo_transactions).to_csv(DEMO_MONTHLY_REVENUE_PATH, index=False)
    calculate_country_summary(demo_transactions).to_csv(DEMO_COUNTRY_SUMMARY_PATH, index=False)
    calculate_product_summary(demo_transactions).to_csv(DEMO_PRODUCT_SUMMARY_PATH, index=False)
    calculate_customer_summary(demo_transactions).to_csv(DEMO_CUSTOMER_SUMMARY_PATH, index=False)


def print_summary(demo_transactions: pd.DataFrame) -> None:
    print("=" * 80)
    print("RETAIL DASHBOARD DEMO DATA SUMMARY")
    print("=" * 80)

    print("\n1. Demo transactions")
    print(f"Rows: {len(demo_transactions):,}")
    print(f"Columns: {demo_transactions.shape[1]:,}")
    print(f"Start date: {demo_transactions['InvoiceDate'].min()}")
    print(f"End date: {demo_transactions['InvoiceDate'].max()}")

    print("\n2. Demo coverage")
    print(f"Countries: {demo_transactions['Country'].nunique():,}")
    print(f"Products: {demo_transactions['StockCode'].nunique():,}")
    print(f"Orders: {demo_transactions['InvoiceNo'].nunique():,}")
    print(
        "Identified customers: "
        f"{demo_transactions.loc[demo_transactions['CustomerIDClean'].ne('Unidentified'), 'CustomerIDClean'].nunique():,}"
    )

    print("\n3. Demo revenue")
    print(f"Total revenue: £{demo_transactions['revenue'].sum():,.2f}")

    print("\n4. Files saved")
    for path in [
        DEMO_TRANSACTIONS_PATH,
        DEMO_KPIS_PATH,
        DEMO_MONTHLY_REVENUE_PATH,
        DEMO_COUNTRY_SUMMARY_PATH,
        DEMO_PRODUCT_SUMMARY_PATH,
        DEMO_CUSTOMER_SUMMARY_PATH,
    ]:
        print(f"- {path}")


if __name__ == "__main__":
    full_transactions = load_transactions()
    demo_data = create_demo_transactions(full_transactions)
    save_demo_data(demo_data)
    print_summary(demo_data)