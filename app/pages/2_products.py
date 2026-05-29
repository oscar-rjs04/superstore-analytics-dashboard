import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.filters import render_filters
from components.kpi_card import kpi_card
from components.charts import bar_chart, line_chart_dual
from queries.product_queries import (
    get_by_category, get_by_subcategory, get_discount_impact, get_category_trend
)
from config import CATEGORY_COLORS

st.set_page_config(page_title="Products", layout="wide")
st.title("Product Analysis")

years, regions, categories = render_filters()
f = (tuple(years), tuple(regions), tuple(categories))

# --- KPIs by category ---
df_cat = get_by_category(*f)
cols = st.columns(len(df_cat))
for col, (_, row) in zip(cols, df_cat.iterrows()):
    kpi_card(col, row["category"], f"${row['revenue']:,.0f}",
             delta=f"{row['margin_pct']:.1f}% margin")

st.divider()

# --- Category trend ---
df_trend = get_category_trend(*f)
fig = line_chart_dual(
    df_trend, x="period", y="revenue",
    year_col="year", month_col="month_name",
    color="category",
    title="Revenue Trend by Category",
    color_discrete_map=CATEGORY_COLORS,
    labels={"revenue": "Revenue (USD)", "period": "Month", "category": "Category"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Sub-category breakdown ---
df_sub = get_by_subcategory(*f)
df_sub["margin_color"] = df_sub["margin_pct"].apply(lambda v: "positive" if v >= 0 else "negative")

sub_col1, sub_col2 = st.columns(2)

with sub_col1:
    fig = bar_chart(
        df_sub, x="revenue", y="sub_category", orientation="h",
        color="category", title="Revenue by Sub-Category",
        color_discrete_map=CATEGORY_COLORS,
        labels={"revenue": "Revenue (USD)", "sub_category": "Sub-Category"},
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)

with sub_col2:
    df_sub_sorted = df_sub.sort_values("margin_pct")
    fig = bar_chart(
        df_sub_sorted, x="margin_pct", y="sub_category", orientation="h",
        color="margin_color", title="Margin % by Sub-Category",
        color_discrete_map={"positive": "#16A34A", "negative": "#DC2626"},
        labels={"margin_pct": "Margin (%)", "sub_category": "Sub-Category", "margin_color": ""},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- Discount impact on margin ---
st.subheader("Discount Impact on Margin")
df_disc = get_discount_impact(*f)
fig = bar_chart(
    df_disc, x="discount_band", y="avg_margin_pct",
    title="Avg Margin % by Discount Band",
    labels={"avg_margin_pct": "Avg Margin (%)", "discount_band": "Discount"},
    color="avg_margin_pct",
    color_continuous_scale="RdYlGn",
)
st.plotly_chart(fig, use_container_width=True)
