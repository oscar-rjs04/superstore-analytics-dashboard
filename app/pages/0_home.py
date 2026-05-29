import streamlit as st

st.markdown("""
<style>
.card {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px 28px;
    margin: 8px 0;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card h3 { margin-top: 0; font-size: 1.05rem; color: #111827; }
.card p  { margin: 0; color: #6B7280; font-size: 0.92rem; }
</style>
""", unsafe_allow_html=True)

st.title("Superstore | Retail Analytics")
st.markdown(
    "Sales, product, geography, customer and supply chain analytics "
    "for the **Superstore** dataset (USA, 2014–2017)."
)
st.info("Use the left menu to navigate between sections.")

st.divider()

def card(col, title, desc):
    col.markdown(f"""
<div class="card">
  <h3>{title}</h3>
  <p>{desc}</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
card(col1, "Sales Overview",  "Global KPIs, monthly trend and shipping mode breakdown.")
card(col2, "Products",        "Margin by category, sub-category and discount impact.")
card(col3, "Geography",       "Revenue map by state and regional analysis.")

col4, col5 = st.columns(2)
card(col4, "Customers",       "Segments, top customers and purchase frequency.")
card(col5, "Supply Chain",    "Inventory, reorder point, purchases vs sales.")
