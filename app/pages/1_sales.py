import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.filters import render_filters
from components.kpi_card import kpi_card
from components.charts import line_chart_dual, bar_chart
from queries.sales_queries import (
    get_kpis, get_monthly_trend, get_sales_by_year,
    get_revenue_by_category_year
)

st.set_page_config(page_title="Sales Overview", layout="wide")
st.title("Sales Overview")

years, regions, categories = render_filters()
f = (tuple(years), tuple(regions), tuple(categories))

# --- KPIs ---
kpis = get_kpis(*f)
c1, c2, c3, c4, c5 = st.columns(5)
kpi_card(c1, "Revenue",          f"${kpis['revenue']:,.0f}")
kpi_card(c2, "Profit",           f"${kpis['profit']:,.0f}")
kpi_card(c3, "Margin",           f"{kpis['margin_pct']:.1f}%")
kpi_card(c4, "Orders",           f"{int(kpis['orders']):,}")
kpi_card(c5, "Avg Order Value",  f"${kpis['aov']:,.2f}")


st.divider()

trend = get_monthly_trend(*f)
fig = line_chart_dual(
    trend, x="period", y=["revenue", "profit"],
    year_col="year", month_col="month_name",
    title="Monthly Revenue & Profit",
    labels={"value": "USD", "variable": "Metric", "period": "Month-Year"},
)
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    df_year = get_sales_by_year(*f)
    df_year["year_str"] = df_year["year"].astype(str)
    fig = bar_chart(
        df_year, x="year_str", y="revenue",
        title="Annual Revenue with YoY Growth",
        color_discrete_sequence=["#3B82F6"],
        labels={"revenue": "Revenue (USD)", "year_str": "Year"},
    )
    for i in range(1, len(df_year)):
        prev = df_year.iloc[i - 1]["revenue"]
        curr = df_year.iloc[i]["revenue"]
        pct  = (curr - prev) / prev * 100
        fig.add_annotation(
            x=df_year.iloc[i]["year_str"],
            y=curr,
            text=f"{pct:+.1f}%",
            showarrow=False,
            yshift=12,
            font=dict(size=11, color="#16A34A" if pct >= 0 else "#DC2626"),
        )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    df_cat_year = get_revenue_by_category_year(*f)
    fig = bar_chart(
        df_cat_year, x="year", y="revenue", color="category",
        title="Revenue by Category & Year",
        barmode="group",
        labels={"revenue": "Revenue (USD)", "category": "Category", "year": "Year"},
    )
    st.plotly_chart(fig, use_container_width=True)
