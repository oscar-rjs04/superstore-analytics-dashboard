import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
import pandas as pd
import streamlit as st
from config import DB_PATH


@st.cache_data
def _load_options():
    conn = sqlite3.connect(DB_PATH)
    years      = pd.read_sql("SELECT DISTINCT year FROM dates ORDER BY year", conn)["year"].tolist()
    regions    = pd.read_sql("SELECT DISTINCT region FROM locations ORDER BY region", conn)["region"].tolist()
    categories = pd.read_sql("SELECT DISTINCT category FROM products ORDER BY category", conn)["category"].tolist()
    conn.close()
    return years, regions, categories


def render_filters() -> tuple[list, list, list]:
    years, regions, categories = _load_options()

    with st.sidebar:
        st.header("Filters")
        sel_years      = st.multiselect("Year",     years,      default=years)
        sel_regions    = st.multiselect("Region",   regions,    default=regions)
        sel_categories = st.multiselect("Category", categories, default=categories)

        if not sel_years:      sel_years      = years
        if not sel_regions:    sel_regions    = regions
        if not sel_categories: sel_categories = categories

    return sel_years, sel_regions, sel_categories
