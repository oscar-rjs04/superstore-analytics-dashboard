import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.filters import render_filters
from components.kpi_card import kpi_card
from components.charts import bar_chart, pie_chart, scatter_chart
from queries.customer_queries import get_by_segment, get_top_customers, get_customer_frequency
from config import SEGMENT_COLORS

st.title("Customer Analysis")

years, regions, categories = render_filters()
f = (tuple(years), tuple(regions), tuple(categories))

# --- KPIs by segment ---
df_seg = get_by_segment(*f)
total_customers = int(df_seg["customers"].sum())
total_orders    = int(df_seg["orders"].sum())

c1, c2, c3 = st.columns(3)
kpi_card(c1, "Total Customers", f"{total_customers:,}")
kpi_card(c2, "Total Orders",    f"{total_orders:,}")
kpi_card(c3, "Avg Orders / Customer", f"{total_orders / total_customers:.1f}")

st.divider()

# --- Segment: pie + bar ---
col1, col2 = st.columns(2)

with col1:
    fig = pie_chart(
        df_seg, names="segment", values="revenue",
        title="Revenue by Segment",
        color="segment", color_discrete_map=SEGMENT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = bar_chart(
        df_seg, x="segment", y="margin_pct",
        color="segment", title="Margin % by Segment",
        color_discrete_map=SEGMENT_COLORS,
        labels={"margin_pct": "Margin (%)", "segment": "Segment"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Top customers ---
df_top = get_top_customers(*f, n=15)
fig = bar_chart(
    df_top, x="revenue", y="customer_name", orientation="h",
    color="segment", title="Top 15 Customers by Revenue",
    color_discrete_map=SEGMENT_COLORS,
    labels={"revenue": "Revenue (USD)", "customer_name": "Customer"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Scatter: frequency vs revenue ---
df_freq = get_customer_frequency(*f)
fig = scatter_chart(
    df_freq, x="total_orders", y="total_revenue",
    color="segment", size="avg_order_value",
    title="Customer Frequency vs Revenue",
    color_discrete_map=SEGMENT_COLORS,
    hover_name="customer_name",
    labels={
        "total_orders":   "Total Orders",
        "total_revenue":  "Total Revenue (USD)",
        "avg_order_value": "Avg Order Value",
    },
)
st.plotly_chart(fig, use_container_width=True)
