from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

DASHBOARD_TRANSACTIONS_PATH = PROCESSED_DATA_DIR / "dashboard_transactions.csv"
EXECUTIVE_KPIS_PATH = PROCESSED_DATA_DIR / "executive_kpis.csv"
MONTHLY_REVENUE_PATH = PROCESSED_DATA_DIR / "monthly_revenue.csv"
COUNTRY_SUMMARY_PATH = PROCESSED_DATA_DIR / "country_summary.csv"
PRODUCT_SUMMARY_PATH = PROCESSED_DATA_DIR / "product_summary.csv"
CUSTOMER_SUMMARY_PATH = PROCESSED_DATA_DIR / "customer_summary.csv"

REQUIRED_FILES = [
    DASHBOARD_TRANSACTIONS_PATH,
    EXECUTIVE_KPIS_PATH,
    MONTHLY_REVENUE_PATH,
    COUNTRY_SUMMARY_PATH,
    PRODUCT_SUMMARY_PATH,
    CUSTOMER_SUMMARY_PATH,
]

OPERATIONAL_STOCK_CODES = {
    "DOT",
    "POST",
    "M",
    "BANK CHARGES",
    "C2",
    "D",
}


def load_processed_data() -> dict[str, pd.DataFrame]:
    """
    Load all processed dashboard datasets.
    """
    missing_files = [path for path in REQUIRED_FILES if not path.exists()]

    if missing_files:
        missing = "\n".join(str(path) for path in missing_files)
        raise FileNotFoundError(
            "Missing processed dashboard files. "
            "Run 'python src/prepare_dashboard_data.py' first.\n"
            f"Missing files:\n{missing}"
        )

    data = {
        "transactions": pd.read_csv(
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
        ),
        "kpis": pd.read_csv(
            EXECUTIVE_KPIS_PATH,
            parse_dates=["start_date", "end_date"],
        ),
        "monthly_revenue": pd.read_csv(
            MONTHLY_REVENUE_PATH,
            dtype={"YearMonth": "str"},
        ),
        "country_summary": pd.read_csv(
            COUNTRY_SUMMARY_PATH,
            dtype={"Country": "str"},
        ),
        "product_summary": pd.read_csv(
            PRODUCT_SUMMARY_PATH,
            dtype={
                "StockCode": "str",
                "Description": "str",
            },
        ),
        "customer_summary": pd.read_csv(
            CUSTOMER_SUMMARY_PATH,
            dtype={"CustomerIDClean": "str"},
        ),
    }

    return data


def assert_non_empty(data: dict[str, pd.DataFrame]) -> None:
    """
    Validate that all processed datasets are non-empty.
    """
    for name, dataset in data.items():
        if dataset.empty:
            raise ValueError(f"{name} dataset is empty.")


def assert_required_columns(data: dict[str, pd.DataFrame]) -> None:
    """
    Validate required columns for dashboard operation.
    """
    required_columns = {
        "transactions": [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "YearMonth",
            "UnitPrice",
            "Revenue",
            "CustomerIDClean",
            "CustomerSegment",
            "Country",
        ],
        "kpis": [
            "total_revenue",
            "total_orders",
            "total_customers",
            "total_countries",
            "total_products",
            "average_order_value",
            "unidentified_revenue",
            "unidentified_revenue_share",
            "start_date",
            "end_date",
        ],
        "monthly_revenue": [
            "YearMonth",
            "revenue",
            "orders",
            "customers",
            "units_sold",
            "average_order_value",
        ],
        "country_summary": [
            "Country",
            "revenue",
            "orders",
            "customers",
            "units_sold",
            "revenue_share",
        ],
        "product_summary": [
            "StockCode",
            "Description",
            "revenue",
            "units_sold",
            "orders",
            "revenue_share",
        ],
        "customer_summary": [
            "CustomerIDClean",
            "revenue",
            "orders",
            "units_sold",
            "countries",
            "revenue_share",
            "cumulative_revenue_share",
        ],
    }

    for dataset_name, columns in required_columns.items():
        missing_columns = [
            column
            for column in columns
            if column not in data[dataset_name].columns
        ]

        if missing_columns:
            raise ValueError(
                f"{dataset_name} is missing required columns: {missing_columns}"
            )


def assert_transaction_quality(transactions: pd.DataFrame) -> None:
    """
    Validate transaction-level dashboard data quality.
    """
    if (transactions["Quantity"] <= 0).any():
        raise ValueError("Dashboard transactions contain non-positive quantities.")

    if (transactions["UnitPrice"] <= 0).any():
        raise ValueError("Dashboard transactions contain non-positive unit prices.")

    if (transactions["Revenue"] <= 0).any():
        raise ValueError("Dashboard transactions contain non-positive revenue.")

    if transactions["InvoiceNo"].isna().any():
        raise ValueError("Dashboard transactions contain missing InvoiceNo.")

    if transactions["InvoiceDate"].isna().any():
        raise ValueError("Dashboard transactions contain missing InvoiceDate.")

    if transactions["Country"].isna().any():
        raise ValueError("Dashboard transactions contain missing Country.")

    expected_revenue = transactions["Quantity"] * transactions["UnitPrice"]
    max_revenue_difference = (transactions["Revenue"] - expected_revenue).abs().max()

    if max_revenue_difference > 0.01:
        raise ValueError(
            "Revenue does not match Quantity * UnitPrice. "
            f"Maximum difference: {max_revenue_difference}"
        )


def assert_reconciliations(data: dict[str, pd.DataFrame]) -> None:
    """
    Validate that summary tables reconcile with transaction-level data.
    """
    transactions = data["transactions"]
    kpis = data["kpis"].iloc[0]
    monthly_revenue = data["monthly_revenue"]
    country_summary = data["country_summary"]
    product_summary = data["product_summary"]
    customer_summary = data["customer_summary"]

    transaction_revenue = transactions["Revenue"].sum()
    transaction_orders = transactions["InvoiceNo"].nunique()
    transaction_customers = transactions.loc[
        transactions["CustomerIDClean"] != "Unknown",
        "CustomerIDClean",
    ].nunique()

    checks = {
        "KPI total revenue": abs(transaction_revenue - kpis["total_revenue"]),
        "Monthly revenue total": abs(transaction_revenue - monthly_revenue["revenue"].sum()),
        "Country revenue total": abs(transaction_revenue - country_summary["revenue"].sum()),
        "Product revenue total": abs(transaction_revenue - product_summary["revenue"].sum()),
    }

    for check_name, difference in checks.items():
        if difference > 0.01:
            raise ValueError(f"{check_name} does not reconcile. Difference: {difference}")

    if transaction_orders != int(kpis["total_orders"]):
        raise ValueError(
            "KPI total_orders does not match transaction-level unique orders."
        )

    if transaction_customers != int(kpis["total_customers"]):
        raise ValueError(
            "KPI total_customers does not match transaction-level unique customers."
        )

    identified_revenue = transactions.loc[
        transactions["CustomerIDClean"] != "Unknown",
        "Revenue",
    ].sum()

    customer_revenue_difference = abs(identified_revenue - customer_summary["revenue"].sum())

    if customer_revenue_difference > 0.01:
        raise ValueError(
            "Customer revenue summary does not reconcile with identified revenue. "
            f"Difference: {customer_revenue_difference}"
        )


def build_executive_diagnostics(data: dict[str, pd.DataFrame]) -> dict:
    """
    Build executive diagnostics for dashboard design.
    """
    transactions = data["transactions"]
    kpis = data["kpis"].iloc[0]
    country_summary = data["country_summary"]
    product_summary = data["product_summary"]
    customer_summary = data["customer_summary"]

    top_country = country_summary.iloc[0]
    top_10_country_share = country_summary.head(10)["revenue_share"].sum()

    top_10_customer_share = customer_summary.head(10)["revenue_share"].sum()
    top_50_customer_share = customer_summary.head(50)["revenue_share"].sum()

    operational_products = product_summary[
        product_summary["StockCode"].isin(OPERATIONAL_STOCK_CODES)
    ].copy()

    operational_revenue_share = operational_products["revenue_share"].sum()

    diagnostics = {
        "total_revenue": float(kpis["total_revenue"]),
        "total_orders": int(kpis["total_orders"]),
        "total_customers": int(kpis["total_customers"]),
        "average_order_value": float(kpis["average_order_value"]),
        "unidentified_revenue_share": float(kpis["unidentified_revenue_share"]),
        "top_country": str(top_country["Country"]),
        "top_country_revenue_share": float(top_country["revenue_share"]),
        "top_10_country_revenue_share": float(top_10_country_share),
        "top_10_customer_revenue_share": float(top_10_customer_share),
        "top_50_customer_revenue_share": float(top_50_customer_share),
        "operational_product_revenue_share": float(operational_revenue_share),
        "date_min": transactions["InvoiceDate"].min(),
        "date_max": transactions["InvoiceDate"].max(),
        "transaction_rows": int(len(transactions)),
    }

    return diagnostics


def print_validation_summary(data: dict[str, pd.DataFrame], diagnostics: dict) -> None:
    """
    Print dashboard data validation summary.
    """
    print("=" * 80)
    print("RETAIL DASHBOARD DATA VALIDATION SUMMARY")
    print("=" * 80)

    print("\n1. Processed dataset shapes")
    for name, dataset in data.items():
        print(f"{name}: {dataset.shape[0]:,} rows, {dataset.shape[1]:,} columns")

    print("\n2. Reconciled KPI snapshot")
    print(f"Total revenue: {diagnostics['total_revenue']:,.2f}")
    print(f"Total orders: {diagnostics['total_orders']:,}")
    print(f"Total customers: {diagnostics['total_customers']:,}")
    print(f"Average order value: {diagnostics['average_order_value']:,.2f}")
    print(
        "Unidentified revenue share: "
        f"{diagnostics['unidentified_revenue_share'] * 100:.2f}%"
    )

    print("\n3. Date coverage")
    print(f"Start date: {diagnostics['date_min']}")
    print(f"End date: {diagnostics['date_max']}")

    print("\n4. Executive concentration diagnostics")
    print(
        f"Top country: {diagnostics['top_country']} "
        f"({diagnostics['top_country_revenue_share'] * 100:.2f}% of revenue)"
    )
    print(
        "Top 10 countries revenue share: "
        f"{diagnostics['top_10_country_revenue_share'] * 100:.2f}%"
    )
    print(
        "Top 10 customers revenue share: "
        f"{diagnostics['top_10_customer_revenue_share'] * 100:.2f}%"
    )
    print(
        "Top 50 customers revenue share: "
        f"{diagnostics['top_50_customer_revenue_share'] * 100:.2f}%"
    )

    print("\n5. Operational stock-code diagnostic")
    print(
        "Operational stock-code revenue share: "
        f"{diagnostics['operational_product_revenue_share'] * 100:.2f}%"
    )

    print("\nValidation result")
    print("All dashboard data validation checks passed.")


if __name__ == "__main__":
    processed_data = load_processed_data()

    assert_non_empty(processed_data)
    assert_required_columns(processed_data)
    assert_transaction_quality(processed_data["transactions"])
    assert_reconciliations(processed_data)

    executive_diagnostics = build_executive_diagnostics(processed_data)

    print_validation_summary(
        data=processed_data,
        diagnostics=executive_diagnostics,
    )