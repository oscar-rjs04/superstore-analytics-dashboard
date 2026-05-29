import streamlit as st

st.set_page_config(
    page_title="Superstore Analytics",
    page_icon=None,
    layout="wide",
)

pg = st.navigation([
    st.Page("pages/0_home.py",         title="Home",           default=True),
    st.Page("pages/1_sales.py",        title="Sales Overview"),
    st.Page("pages/2_products.py",     title="Products"),
    st.Page("pages/3_geography.py",    title="Geography"),
    st.Page("pages/4_customers.py",    title="Customers"),
    st.Page("pages/5_supply_chain.py", title="Supply Chain"),
])

pg.run()