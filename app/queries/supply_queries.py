import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
import pandas as pd
import streamlit as st
from config import DB_PATH


def _conn():
    return sqlite3.connect(DB_PATH)


def _ph(items):
    return ",".join("?" * len(items))


@st.cache_data
def get_inventory_by_subcategory(categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            p.category,
            p.sub_category,
            ROUND(AVG(i.stock_qty), 1)     AS avg_stock,
            ROUND(AVG(i.reorder_point), 1) AS avg_reorder_point,
            ROUND(AVG(i.days_of_stock), 1) AS avg_days_of_stock,
            COUNT(CASE WHEN i.stock_qty < i.reorder_point THEN 1 END) AS low_stock_snapshots
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE p.category IN ({_ph(categories)})
        GROUP BY p.category, p.sub_category
        ORDER BY avg_days_of_stock ASC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(categories))
    conn.close()
    return df


@st.cache_data
def get_low_stock_products(categories: tuple, snapshot_date: str = "2017-09-01") -> pd.DataFrame:
    sql = f"""
        SELECT
            i.product_id,
            p.category,
            p.sub_category,
            ROUND(i.stock_qty, 0)                       AS stock_qty,
            ROUND(i.reorder_point, 1)                   AS reorder_point,
            ROUND(i.days_of_stock, 1)                   AS days_of_stock,
            ROUND(i.stock_qty - i.reorder_point, 2)     AS stock_gap
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.snapshot_date = ?
          AND i.stock_qty <= i.reorder_point
          AND p.category IN ({_ph(categories)})
        ORDER BY stock_gap ASC
        LIMIT 20
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=[snapshot_date] + list(categories))
    conn.close()
    return df


@st.cache_data
def get_monthly_purchases_vs_sales(categories: tuple) -> pd.DataFrame:
    conn = _conn()
    purchases = pd.read_sql(f"""
        SELECT
            strftime('%Y-%m', pu.purchase_date) AS period,
            p.category,
            ROUND(SUM(pu.total_cost), 2)        AS purchase_cost
        FROM purchases pu
        JOIN products p ON pu.product_id = p.product_id
        WHERE p.category IN ({_ph(categories)})
        GROUP BY period, p.category
        ORDER BY period
    """, conn, params=list(categories))

    sales = pd.read_sql(f"""
        SELECT
            strftime('%Y-%m', s.order_date) AS period,
            p.category,
            ROUND(SUM(s.sales), 2)          AS revenue,
            ROUND(SUM(s.cost), 2)           AS cogs
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE p.category IN ({_ph(categories)})
        GROUP BY period, p.category
        ORDER BY period
    """, conn, params=list(categories))
    conn.close()

    return purchases.merge(sales, on=["period", "category"], how="outer").fillna(0)


@st.cache_data
def get_supplier_summary(categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            su.supplier_name,
            su.category,
            COUNT(pu.purchase_id)        AS total_orders,
            ROUND(SUM(pu.total_cost), 2) AS total_spend,
            ROUND(AVG(pu.unit_cost), 4)  AS avg_unit_cost
        FROM purchases pu
        JOIN suppliers su ON pu.supplier_id = su.supplier_id
        JOIN products p   ON pu.product_id  = p.product_id
        WHERE su.category IN ({_ph(categories)})
        GROUP BY su.supplier_name, su.category
        ORDER BY total_spend DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(categories))
    conn.close()
    return df

@st.cache_data
def get_sales_by_ship_mode(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            s.ship_mode,
            ROUND(SUM(s.sales), 2)     AS revenue,
            COUNT(DISTINCT s.order_id) AS orders
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY s.ship_mode
        ORDER BY revenue DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df