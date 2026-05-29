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
def get_category_trend(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            p.category,
            d.year,
            d.month_name,
            ROUND(SUM(s.sales), 2) AS revenue
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY p.category, d.year, d.month
        ORDER BY d.year, d.month
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    df["period"] = df["year"].astype(str) + "-" + df["month_name"].astype(str).str.zfill(2)
    return df


@st.cache_data
def get_by_category(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            p.category,
            ROUND(SUM(s.sales), 2)                        AS revenue,
            ROUND(SUM(s.profit), 2)                       AS profit,
            ROUND(SUM(s.profit) / SUM(s.sales) * 100, 1) AS margin_pct,
            COUNT(DISTINCT s.order_id)                    AS orders
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY p.category
        ORDER BY revenue DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df


@st.cache_data
def get_by_subcategory(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            p.category,
            p.sub_category,
            ROUND(SUM(s.sales), 2)                        AS revenue,
            ROUND(SUM(s.profit), 2)                       AS profit,
            ROUND(SUM(s.profit) / SUM(s.sales) * 100, 1) AS margin_pct,
            SUM(s.quantity)                               AS units_sold
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY p.category, p.sub_category
        ORDER BY revenue DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df


@st.cache_data
def get_top_products(years: tuple, regions: tuple, categories: tuple, n: int = 10) -> pd.DataFrame:
    sql = f"""
        SELECT
            s.product_id,
            p.category,
            p.sub_category,
            ROUND(SUM(s.sales), 2)  AS revenue,
            ROUND(SUM(s.profit), 2) AS profit,
            SUM(s.quantity)         AS units_sold
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY s.product_id, p.category, p.sub_category
        ORDER BY revenue DESC
        LIMIT {n}
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df


@st.cache_data
def get_discount_impact(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            CASE
                WHEN s.discount = 0     THEN '0%'
                WHEN s.discount <= 0.10 THEN '1–10%'
                WHEN s.discount <= 0.20 THEN '11–20%'
                WHEN s.discount <= 0.30 THEN '21–30%'
                WHEN s.discount <= 0.40 THEN '31–40%'
                WHEN s.discount <= 0.50 THEN '41–50%'
                ELSE '> 50%'
            END                                          AS discount_band,
            ROUND(AVG(s.profit / s.sales) * 100, 1)     AS avg_margin_pct,
            COUNT(*)                                     AS transactions
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY discount_band
        ORDER BY MIN(s.discount)
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df
