# Retail Executive Dashboard: Business Performance Monitoring with Streamlit

## Overview

This project builds an interactive executive dashboard to monitor retail sales performance.

The goal is to transform transactional retail data into a decision-oriented dashboard with KPIs, trend analysis, country exposure, product ranking, customer concentration diagnostics, and executive alerts.

The dashboard is built with Streamlit, pandas, Plotly, and reproducible Python data preparation scripts.

The app supports two data modes:

- **Full local processed data** for complete local analysis.
- **Public demo data** for lightweight public deployment.

---

## Live Demo

The dashboard is deployed on Streamlit Community Cloud:

```text
https://retail-executive-dashboard-8xbvujcjstgigvpkheppaj.streamlit.app/
```

The public deployment uses the lightweight demo data layer stored in `data/demo/`.

For full local analysis, run the complete data pipeline with the raw dataset and use `data/processed/`.

---

## Business Context

Executives need fast visibility into commercial performance.

A useful dashboard should not only show charts. It should help decision-makers understand:

- how much revenue was generated,
- which markets dominate performance,
- which products drive sales,
- how concentrated revenue is across customers,
- how much revenue lacks customer identification,
- whether operational stock codes affect product rankings,
- whether period comparisons are valid.

This dashboard focuses on clear executive monitoring rather than accounting reconciliation.

---

## Main Business Questions

The dashboard answers the following questions:

1. How much revenue was generated?
2. How many orders, customers, units, and countries are represented?
3. How does revenue evolve over time?
4. Which countries generate the most revenue?
5. Which products generate the most revenue?
6. How concentrated is revenue among top customers?
7. How much revenue has no identified customer?
8. Are product rankings affected by operational stock codes?
9. Are there period coverage issues that may distort interpretation?

---

## Dataset

This project uses the Online Retail dataset.

The raw dataset contains transactional sales records with invoice, product, quantity, price, customer, date, and country fields.

Expected raw file:

```text
data/raw/online_retail.csv
```

Expected columns:

| Column | Description |
|---|---|
| `InvoiceNo` | Invoice identifier |
| `StockCode` | Product or operational code |
| `Description` | Product description |
| `Quantity` | Quantity purchased |
| `InvoiceDate` | Invoice timestamp |
| `UnitPrice` | Unit price |
| `CustomerID` | Customer identifier |
| `Country` | Customer country |

> Raw data is not included in this repository. Place `online_retail.csv` inside `data/raw/` before running the full local pipeline.

---

## Raw Data Summary

| Metric | Value |
|---|---:|
| Rows | 541,909 |
| Columns | 8 |
| Unique invoices | 25,900 |
| Cancellation rows | 9,288 |
| Unique customers | 4,372 |
| Rows without CustomerID | 135,080 |
| Countries | 38 |
| Date range | 2010-12-01 to 2011-12-09 |

The raw data includes cancellations, negative quantities, non-positive prices, duplicate rows, and transactions without customer identifiers.

---

## Dashboard Data Scope

The dashboard uses **valid sales transactions only**.

Excluded from the full local dashboard data layer:

- cancelled invoices,
- non-positive quantities,
- non-positive unit prices,
- exact duplicate rows.

Revenue is calculated as:

```text
Revenue = Quantity × UnitPrice
```

Customer concentration analysis excludes unidentified customers.

Product ranking can optionally exclude operational stock codes from the dashboard interface.

---

## Processed Data Summary

After cleaning and filtering the full dataset:

| Metric | Value |
|---|---:|
| Initial rows | 541,909 |
| Duplicate rows removed | 5,268 |
| Rows after deduplication | 536,641 |
| Cancellation rows excluded | 9,251 |
| Non-positive quantity rows excluded | 10,587 |
| Non-positive price rows excluded | 2,512 |
| Valid sales rows | 524,878 |

---

## Executive KPI Snapshot

Full local processed data produces the following KPI baseline:

| KPI | Value |
|---|---:|
| Total revenue | £10,642,110.80 |
| Total orders | 19,960 |
| Total identified customers | 4,338 |
| Total countries | 38 |
| Total products | 3,922 |
| Average order value | £533.17 |
| Unidentified revenue | £1,754,901.91 |
| Unidentified revenue share | 16.49% |

---

## Key Executive Findings

### 1. Revenue is highly concentrated in the United Kingdom

The United Kingdom represents approximately **84.59%** of valid sales revenue.

This means global conclusions are heavily dominated by one market. Any international analysis should separate UK and non-UK views.

### 2. Top countries dominate revenue

The top 10 countries represent approximately **97.21%** of total revenue.

This indicates strong geographic concentration and limited revenue dispersion across the remaining countries.

### 3. Customer visibility is incomplete

Approximately **16.49%** of revenue has no identified customer.

This limits customer-level analysis and should be considered when interpreting customer concentration.

### 4. Customer concentration exists

Among identified customers:

| Group | Revenue Share |
|---|---:|
| Top 10 customers | 17.30% |
| Top 50 customers | 33.30% |

This creates retention exposure concentrated in a relatively small customer group.

### 5. Operational stock codes affect product rankings

Operational stock codes represent approximately **3.47%** of revenue.

Examples include:

- `DOT`
- `POST`
- `M`
- `BANK CHARGES`
- `C2`
- `D`

The dashboard includes a filter to exclude these codes from product rankings.

### 6. Period coverage requires caution

The dataset starts on 2010-12-01 and ends on 2011-12-09.

The final month is partial. A decline in December 2011 should not be interpreted as a full-month commercial decline without checking coverage.

---

## Dashboard Features

The Streamlit dashboard includes:

- BI-style light theme,
- executive KPI cards,
- date range filter,
- country view selector,
- country modes:
  - All countries,
  - United Kingdom only,
  - Exclude United Kingdom,
  - Top international markets,
  - Custom selection,
- optional exclusion of operational stock codes from product ranking,
- revenue trend chart,
- country revenue mix chart,
- top product ranking,
- customer concentration curve,
- top customer concentration KPIs,
- detailed country/product/customer tables,
- data scope and assumptions section,
- automatic data-source fallback for public deployment.

---

## Project Structure

```text
retail-executive-dashboard/
├── app/
│   └── app.py
├── data/
│   ├── demo/
│   │   ├── country_summary.csv
│   │   ├── customer_summary.csv
│   │   ├── dashboard_transactions.csv
│   │   ├── executive_kpis.csv
│   │   ├── monthly_revenue.csv
│   │   └── product_summary.csv
│   ├── raw/
│   └── processed/
├── reports/
│   └── figures/
├── src/
│   ├── create_demo_data.py
│   ├── load_data.py
│   ├── prepare_dashboard_data.py
│   └── validate_dashboard_data.py
├── .streamlit/
│   └── config.toml
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Pipeline

The project has four reproducible data scripts.

### 1. Load raw data

```bash
python src/load_data.py
```

This script checks that the raw dataset exists and prints a basic raw data profile.

### 2. Prepare dashboard data

```bash
python src/prepare_dashboard_data.py
```

This script creates the full processed dashboard tables:

```text
data/processed/dashboard_transactions.csv
data/processed/executive_kpis.csv
data/processed/monthly_revenue.csv
data/processed/country_summary.csv
data/processed/product_summary.csv
data/processed/customer_summary.csv
```

These full processed files are generated locally and are ignored by Git.

### 3. Validate dashboard data

```bash
python src/validate_dashboard_data.py
```

This script validates:

- required processed files,
- required columns,
- non-empty datasets,
- positive quantity, price, and revenue,
- KPI reconciliation,
- monthly revenue reconciliation,
- country revenue reconciliation,
- product revenue reconciliation,
- customer revenue reconciliation,
- executive concentration diagnostics.

The validation must pass before considering the full local data layer valid.

### 4. Create public demo data

```bash
python src/create_demo_data.py
```

This script creates a compact public demo dataset from the full processed transaction layer.

It generates:

```text
data/demo/dashboard_transactions.csv
data/demo/executive_kpis.csv
data/demo/monthly_revenue.csv
data/demo/country_summary.csv
data/demo/product_summary.csv
data/demo/customer_summary.csv
```

The demo data is committed to GitHub so the dashboard can run in public deployment environments without the full raw or processed dataset.

---

## Public Demo Data

This dashboard supports two data modes.

### Full local processed data

Used when all required files exist in:

```text
data/processed/
```

This mode is intended for complete local analysis.

It is generated with:

```bash
python src/prepare_dashboard_data.py
```

### Public demo data

Used automatically when the full processed files are not available.

It is stored in:

```text
data/demo/
```

The demo data is a compact sample generated from the processed dashboard transactions. It preserves:

- date coverage,
- country coverage,
- product variety,
- customer variety,
- dashboard filters,
- chart functionality,
- table functionality.

The app automatically resolves the data source:

```text
data/processed/ → preferred for full local analysis
data/demo/      → fallback for public deployment
```

The active data source is shown in the sidebar.

---

## Demo Data Summary

The current public demo dataset contains:

| Metric | Value |
|---|---:|
| Demo transaction rows | 6,667 |
| Countries | 38 |
| Products | 2,010 |
| Orders | 3,671 |
| Identified customers | 1,592 |
| Demo revenue | £215,745.43 |
| Date range | 2010-12-01 to 2011-12-09 |

The demo dataset is designed for public demonstration. It should not be interpreted as the full business result.

---

## How to Run the Dashboard Locally

### 1. Clone the repository

```bash
git clone https://github.com/RommelPa/retail-executive-dashboard.git
cd retail-executive-dashboard
```

### 2. Create a virtual environment

```bash
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add raw data for full local mode

Place the dataset here:

```text
data/raw/online_retail.csv
```

### 5. Run the full local data pipeline

```bash
python src/load_data.py
python src/prepare_dashboard_data.py
python src/validate_dashboard_data.py
```

### 6. Run the Streamlit app

```bash
streamlit run app/app.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

If full processed data is available, the sidebar shows:

```text
Data source: Full local processed data
```

If full processed data is not available, the dashboard falls back to public demo data and the sidebar shows:

```text
Data source: Public demo data
```

---

## Deployment Notes

The dashboard is deployed on Streamlit Community Cloud.

Live app:

```text
https://retail-executive-dashboard-8xbvujcjstgigvpkheppaj.streamlit.app/
```

Deployment configuration:

```text
Repository: RommelPa/retail-executive-dashboard
Branch: main
Main file path: app/app.py
```

The public deployment uses `data/demo/` by default because the full processed transaction file is intentionally not committed to GitHub.

This keeps the repository lightweight while still allowing the dashboard to run publicly.

---

## Reproducibility Check

Before considering the dashboard valid, run:

```bash
python -m py_compile app/app.py src/load_data.py src/prepare_dashboard_data.py src/validate_dashboard_data.py src/create_demo_data.py
python src/load_data.py
python src/prepare_dashboard_data.py
python src/validate_dashboard_data.py
python src/create_demo_data.py
streamlit run app/app.py
```

Expected validation result:

```text
Validation result
All dashboard data validation checks passed.
```

Expected app behavior:

```text
Data source: Full local processed data
```

To simulate public deployment mode locally, temporarily move the full processed CSV files out of `data/processed/`. The app should fall back to:

```text
Data source: Public demo data
```

---

## Tools Used

- Python
- pandas
- Plotly
- Streamlit
- openpyxl
- Streamlit Community Cloud
- Git
- GitHub

---

## Design Decisions

### Why Streamlit?

Streamlit was selected because it allows the dashboard to be reproduced from code, reviewed on GitHub, and deployed as a lightweight web app.

### Why not Power BI for this project?

Power BI is excellent for enterprise BI, but `.pbix` files are less transparent in a GitHub portfolio. A Streamlit dashboard makes the data pipeline, validation logic, and visualization code fully inspectable.

### Why exclude cancellations and non-positive transactions?

The first version focuses on valid sales monitoring. Returns, cancellations, and adjustment analysis can be added as a separate dashboard module in a future version.

### Why include operational stock-code filtering?

Codes such as postage and manual charges can materially affect product rankings. The dashboard allows users to view product rankings with or without those operational codes.

### Why include demo data?

The full processed transaction file is too large for a clean portfolio deployment workflow.

The demo data keeps the repository lightweight and makes the dashboard deployable without requiring private local data files.

### Why use automatic data fallback?

The same app can support both local full analysis and public demo deployment.

This avoids maintaining separate local and deployment versions of the dashboard.

---

## Limitations

- The dashboard uses a historical retail dataset and is not connected to live systems.
- The first and last dataset months may be partial.
- Revenue is based on transaction values and is not a full accounting ledger.
- Returns and cancellations are excluded from the v1 dashboard layer.
- Customer concentration excludes unidentified customers.
- Country and product analysis can be dominated by the United Kingdom.
- Operational stock codes can affect product rankings if not excluded.
- The public deployment uses compact demo data, not the full processed transaction layer.
- Demo data is intended to demonstrate dashboard functionality, not reproduce full-data KPIs.
- The dashboard is designed for executive monitoring, not audit-grade financial reporting.

---

## Next Steps

Possible extensions:

- add return and cancellation analysis,
- add cohort-style customer retention views,
- add product category mapping,
- add downloadable filtered data,
- add revenue comparison by selected period,
- add a dedicated non-UK international performance view,
- add authentication for private business deployment.

---

## Spanish Summary

Este proyecto construye un dashboard ejecutivo retail con Streamlit, pandas y Plotly.

El dashboard transforma datos transaccionales en una herramienta de monitoreo comercial con KPIs, tendencia de revenue, concentración por país, ranking de productos, concentración de clientes y diagnóstico ejecutivo.

El proyecto incluye carga de datos, preparación de una capa limpia para dashboard, validaciones de reconciliación, app interactiva tipo BI, filtros ejecutivos, documentación reproducible, una capa demo pública para despliegue y una demo pública en Streamlit Community Cloud.

Demo pública:

```text
https://retail-executive-dashboard-8xbvujcjstgigvpkheppaj.streamlit.app/
```

Hallazgos principales con datos completos locales:

- revenue total validado: £10.64M,
- 19,960 órdenes válidas,
- 4,338 clientes identificados,
- Reino Unido concentra 84.59% del revenue,
- 16.49% del revenue no tiene cliente identificado,
- top 10 clientes concentran 17.30% del revenue identificado,
- códigos operativos representan 3.47% del revenue.

La app soporta dos modos:

- datos completos locales en `data/processed/`,
- datos demo públicos en `data/demo/`.

La app está diseñada para monitoreo ejecutivo, no para conciliación contable.