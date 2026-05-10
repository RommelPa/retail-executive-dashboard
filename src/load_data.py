from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail.csv"

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
    Load the raw Online Retail dataset.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data file not found at {path}.\n\n"
            "Copy online_retail.csv from the retail-sales-eda project "
            "or download the Online Retail dataset and place it inside data/raw/."
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


def validate_columns(data: pd.DataFrame) -> None:
    """
    Validate expected raw dataset columns.
    """
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in data.columns]

    if missing_columns:
        raise ValueError(
            "The dataset is missing expected columns:\n"
            f"{missing_columns}"
        )


def validate_basic_content(data: pd.DataFrame) -> None:
    """
    Validate basic dataset content.
    """
    if data.empty:
        raise ValueError("The dataset is empty.")

    if data["InvoiceNo"].isna().any():
        raise ValueError("InvoiceNo contains missing values.")

    if data["InvoiceDate"].isna().any():
        raise ValueError("InvoiceDate contains invalid or missing values.")

    if data["Quantity"].isna().any():
        raise ValueError("Quantity contains missing values.")

    if data["UnitPrice"].isna().any():
        raise ValueError("UnitPrice contains missing values.")


if __name__ == "__main__":
    retail_data = load_raw_data()
    validate_columns(retail_data)
    validate_basic_content(retail_data)

    print("Raw Online Retail dataset loaded successfully.")
    print(f"Path: {RAW_DATA_PATH}")
    print(f"Rows: {retail_data.shape[0]:,}")
    print(f"Columns: {retail_data.shape[1]:,}")

    print("\nColumn names:")
    print(list(retail_data.columns))

    print("\nDate range:")
    print(f"Minimum InvoiceDate: {retail_data['InvoiceDate'].min()}")
    print(f"Maximum InvoiceDate: {retail_data['InvoiceDate'].max()}")

    print("\nInvoice analysis:")
    print(f"Unique invoices: {retail_data['InvoiceNo'].nunique():,}")
    print(f"Cancellation rows: {retail_data['InvoiceNo'].str.startswith('C', na=False).sum():,}")

    print("\nCustomer analysis:")
    print(f"Unique customers: {retail_data['CustomerID'].nunique():,}")
    print(f"Rows without CustomerID: {retail_data['CustomerID'].isna().sum():,}")

    print("\nCountry analysis:")
    print(f"Unique countries: {retail_data['Country'].nunique():,}")
    print(retail_data["Country"].value_counts().head(10))

    print("\nQuantity summary:")
    print(retail_data["Quantity"].describe())

    print("\nUnitPrice summary:")
    print(retail_data["UnitPrice"].describe())

    print("\nSample rows:")
    print(retail_data.head())