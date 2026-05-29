import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.filters import render_filters
from components.kpi_card import kpi_card
from components.charts import bar_chart, line_chart
from queries.supply_queries import (
    get_inventory_by_subcategory, get_low_stock_products,
    get_monthly_purchases_vs_sales, get_supplier_summary,
    get_sales_by_ship_mode
)
from config import CATEGORY_COLORS, PALETTE

st.set_page_config(page_title="Supply Chain", layout="wide")
st.title("Supply Chain")

years, regions, categories = render_filters()
f = (tuple(years), tuple(regions), tuple(categories))
cat_filter = tuple(categories)

# --- Inventory KPIs ---
df_inv = get_inventory_by_subcategory(cat_filter)
df_low = get_low_stock_products(cat_filter)

c1, c2, c3 = st.columns(3)
kpi_card(c1, "Sub-Categories Tracked", f"{len(df_inv)}")
kpi_card(c2, "Products Below Reorder Point", f"{len(df_low)}", delta_color="inverse" if len(df_low) > 0 else "normal")
kpi_card(c3, "Avg Days of Stock", f"{df_inv['avg_days_of_stock'].mean():.0f} days")

st.divider()

# --- Days of stock by sub-category ---
fig = bar_chart(
    df_inv, x="avg_days_of_stock", y="sub_category", orientation="h",
    color="category", title="Avg Days of Stock by Sub-Category",
    color_discrete_map=CATEGORY_COLORS,
    labels={"avg_days_of_stock": "Avg Days of Stock", "sub_category": "Sub-Category"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Products below reorder point ---
st.subheader("Products Below Reorder Point (latest snapshot)")
if df_low.empty:
    st.success("No products below reorder point.")
else:
    st.dataframe(df_low, use_container_width=True)

st.divider()

# --- Monthly purchases vs sales ---
df_pvs = get_monthly_purchases_vs_sales(cat_filter)
col1, col2 = st.columns(2)

with col1:
    fig = line_chart(
        df_pvs[df_pvs["category"] == categories[0]] if categories else df_pvs,
        x="period", y=["purchase_cost", "cogs"],
        title="Purchases Cost vs COGS (monthly)",
        labels={"value": "USD", "variable": "Metric", "period": "Month"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_sup = get_supplier_summary(cat_filter)
    fig = bar_chart(
        df_sup, x="total_spend", y="supplier_name", orientation="h",
        color="category", title="Total Spend by Supplier",
        color_discrete_map=CATEGORY_COLORS,
        labels={"total_spend": "Total Spend (USD)", "supplier_name": "Supplier"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Ship Mode ---
ship = get_sales_by_ship_mode(*f)
fig = bar_chart(
    ship, x="revenue", y="ship_mode", orientation="h",
    title="Revenue by Ship Mode",
    color_discrete_sequence=[PALETTE["primary"]],
    labels={"revenue": "Revenue (USD)", "ship_mode": "Ship Mode"},
)
st.plotly_chart(fig, use_container_width=True)
