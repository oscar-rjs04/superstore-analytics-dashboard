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
def get_by_region(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            l.region,
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
        GROUP BY l.region
        ORDER BY revenue DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df


@st.cache_data
def get_by_state(years: tuple, regions: tuple, categories: tuple) -> pd.DataFrame:
    sql = f"""
        SELECT
            l.state,
            l.region,
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
        GROUP BY l.state, l.region
        ORDER BY revenue DESC
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df


@st.cache_data
def get_top_cities(years: tuple, regions: tuple, categories: tuple, n: int = 15) -> pd.DataFrame:
    sql = f"""
        SELECT
            l.city,
            l.state,
            l.region,
            ROUND(SUM(s.sales), 2)  AS revenue,
            ROUND(SUM(s.profit), 2) AS profit
        FROM sales s
        JOIN dates d     ON s.order_date  = d.date
        JOIN locations l ON s.postal_code = l.postal_code
        JOIN products p  ON s.product_id  = p.product_id
        WHERE d.year     IN ({_ph(years)})
          AND l.region   IN ({_ph(regions)})
          AND p.category IN ({_ph(categories)})
        GROUP BY l.city, l.state, l.region
        ORDER BY revenue DESC
        LIMIT {n}
    """
    conn = _conn()
    df = pd.read_sql(sql, conn, params=list(years) + list(regions) + list(categories))
    conn.close()
    return df
