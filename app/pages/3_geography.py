import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.filters import render_filters
from components.kpi_card import kpi_card
from components.charts import bar_chart, choropleth_us
from queries.geo_queries import get_by_region, get_by_state, get_top_cities
from config import REGION_COLORS, STATE_ABBREV

st.set_page_config(page_title="Geography", layout="wide")
st.title("Geographic Analysis")

years, regions, categories = render_filters()
f = (tuple(years), tuple(regions), tuple(categories))

# --- KPIs by region ---
df_region = get_by_region(*f)
cols = st.columns(len(df_region))
for col, (_, row) in zip(cols, df_region.iterrows()):
    kpi_card(col, row["region"], f"${row['revenue']:,.0f}",
             delta=f"{row['margin_pct']:.1f}% margin")

st.divider()

# --- Choropleth map ---
df_state = get_by_state(*f)
df_state["state_abbrev"] = df_state["state"].map(STATE_ABBREV)

map_metric = st.radio(
    "Map metric", ["Revenue", "Margin %"],
    horizontal=True, label_visibility="collapsed",
)

if map_metric == "Revenue":
    fig = choropleth_us(
        df_state, locations="state_abbrev", color="revenue",
        title="Revenue by State",
        color_continuous_scale="Blues",
        labels={"revenue": "Revenue (USD)"},
    )
else:
    fig = choropleth_us(
        df_state, locations="state_abbrev", color="margin_pct",
        title="Margin % by State",
        color_continuous_scale="RdYlGn",
        labels={"margin_pct": "Margin (%)"},
    )
st.plotly_chart(fig, use_container_width=True)

# --- Region + top cities ---
col1, col2 = st.columns(2)

with col1:
    fig = bar_chart(
        df_region, x="region", y="revenue",
        color="region", title="Revenue by Region",
        color_discrete_map=REGION_COLORS,
        labels={"revenue": "Revenue (USD)", "region": "Region"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_cities = get_top_cities(*f, n=15)
    fig = bar_chart(
        df_cities, x="revenue", y="city", orientation="h",
        color="region", title="Top 15 Cities by Revenue",
        color_discrete_map=REGION_COLORS,
        labels={"revenue": "Revenue (USD)", "city": "City"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- State table ---
st.subheader("Revenue & Profit by State")
st.dataframe(
    df_state[["state", "region", "revenue", "profit", "margin_pct", "orders"]]
    .sort_values("revenue", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
)
