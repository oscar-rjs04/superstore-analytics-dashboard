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
def get_kpis(years: tuple, regions: tuple, categories: tuple) -> dict:
    sql = f"""
        SELECT
            ROUND(SUM(s.sales), 2)                              AS revenue,
            ROUND(SUM(s.profit), 2)                             AS profit,
            ROUND(SUM(s.profit) / SUM(s.sales) * 100, 1)       AS margin_pct,
            COUNT(DISTINCT s.order_id)                          AS orders,
            ROUND(SUM(s.sales) / COUNT(DISTINCT s.order_id), 2) AS aov
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
    """
    conn = _conn()
    row = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return row.iloc[0].to_dict()


@st.cache_data
def get_monthly_trend(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            d.year,
            d.month_name,
            ROUND(SUM(s.sales), 2)  AS revenue,
            ROUND(SUM(s.profit), 2) AS profit
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    df["period"] = df["year"].astype(str) + "-" + df["month_name"].astype(str).str.zfill(2)
    return df

@st.cache_data
def get_revenue_by_category_year(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            p.category,
            d.year,
            ROUND(SUM(s.sales), 2) AS revenue
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY p.category, d.year
        ORDER BY p.category, d.year
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    df["year"] = df["year"].astype(str)
    return df


@st.cache_data
def get_sales_by_year(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            d.year,
            ROUND(SUM(s.sales), 2)     AS revenue,
            ROUND(SUM(s.profit), 2)    AS profit,
            COUNT(DISTINCT s.order_id) AS orders
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY d.year
        ORDER BY d.year
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df
