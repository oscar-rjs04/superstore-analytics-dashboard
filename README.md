# Superstore Retail Analytics Dashboard

An end-to-end data analytics portfolio project built on the public [Superstore](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) dataset (US retail sales, 2014–2017).

## Overview

The project covers the full analytics pipeline: raw data ingestion, ETL into a star-schema SQLite database, and an interactive Streamlit dashboard with five analysis sections.

## Dashboard Sections

| Section | Content |
|---|---|
| Sales Overview | Revenue, profit, margin KPIs — monthly trend and shipping mode breakdown |
| Products | Margin by category and sub-category, discount impact analysis |
| Geography | Revenue choropleth map by state, regional and city breakdown |
| Customers | Segment analysis, top customers, purchase frequency scatter |
| Supply Chain | Inventory levels, days of stock, reorder points, purchases vs. COGS |

## Stack

- **Python 3.13**
- **pandas / numpy** — ETL and synthetic data generation
- **SQLite** — local star-schema database (8 tables, ~180k rows)
- **Streamlit** — interactive dashboard
- **Plotly** — charts and visualizations

## Data Model

Star schema with 3 fact tables and 5 dimension tables.

**Fact tables:** `sales` (9,994 rows), `purchases` (83,565 rows), `inventory` (83,790 rows)

**Dimension tables:** `customers`, `products`, `locations`, `dates`, `suppliers`

> Purchases and inventory data are synthetically generated with realistic lead times, reorder points, and month-over-month stock calculations. Sales data is from the original Superstore CSV.

## Project Structure

```
├── app/
│   ├── app.py                  # Streamlit entry point
│   ├── components/             # Reusable UI components (charts, KPI cards, filters)
│   ├── pages/                  # One file per dashboard section
│   └── queries/                # SQL queries with caching, one module per section
├── data/
│   ├── raw/                    # Original Superstore.csv (latin-1 encoding)
│   └── processed/              # CSVs exported from SQLite
├── database/
│   └── superstore.db           # SQLite database
└── etl/
    ├── download_data.py        # Kaggle download via kagglehub
    ├── etl_sales.py            # Raw CSV to star schema
    ├── generate_synthetic.py   # Purchases and inventory generation
    └── export_csv.py           # SQLite to CSV export
```

## Running Locally

**1. Clone the repository**

```bash
git clone https://github.com/oscar-rjs04/dashboard-superstore.git
cd dashboard-superstore
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the ETL pipeline** *(only needed if the database is not included)*

```bash
python etl/download_data.py
python etl/etl_sales.py
python etl/generate_synthetic.py
```

**5. Launch the dashboard**

```bash
streamlit run app/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.