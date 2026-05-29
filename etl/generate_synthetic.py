import os
import sqlite3

import numpy as np
import pandas as pd

DB_PATH = "database/superstore.db"

np.random.seed(42)

# --- Lead times por categoria (dias) ---
LEAD_TIMES = {
    "Furniture": 21,
    "Office Supplies": 10,
    "Technology": 14
}

# --- Suppliers por categoria ---
SUPPLIERS = {
    "Furniture": ["Steelcase Supply Co.", "Herman Miller Dist.", "HON Industries"],
    "Office Supplies": ["Avery Wholesale", "3M Distribution", "Esselte Group", "ACCO Brands"],
    "Technology": ["Ingram Micro", "Tech Data Corp.", "D&H Distributing"]
}

def load_tables(conn):
    sales = pd.read_sql("SELECT * FROM sales", conn)
    products = pd.read_sql("SELECT * FROM products", conn)
    sales["order_date"] = pd.to_datetime(sales["order_date"])
    sales["ship_date"] = pd.to_datetime(sales["ship_date"])
    return sales, products

def build_suppliers():
    rows = []
    supplier_id = 1
    for category, names in SUPPLIERS.items():
        for name in names:
            rows.append({
                "supplier_id": f"SUP-{supplier_id:03d}",
                "supplier_name": name,
                "category": category
            })
            supplier_id += 1
    return pd.DataFrame(rows)

def build_purchases(sales, products, suppliers):
    # Costo unitario promedio por producto
    sales["unit_cost"] = sales["cost"] / sales["quantity"]
    unit_cost_avg = (
        sales.groupby("product_id")["unit_cost"]
        .mean()
        .reset_index()
        .rename(columns={"unit_cost": "avg_unit_cost"})
    )

    # Velocidad de ventas mensual por producto — excluir mes incompleto
    sales["year_month"] = sales["order_date"].dt.to_period("M")
    monthly_qty = (
        sales[sales["year_month"] != pd.Period("2017-09", "M")]  # <- excluir sep 2017
        .groupby(["product_id", "year_month"])["quantity"]
        .sum()
        .reset_index()
    )
    avg_monthly_qty = (
        monthly_qty.groupby("product_id")["quantity"]
        .mean()
        .reset_index()
        .rename(columns={"quantity": "avg_monthly_qty"})
    )

    # Merge con productos
    prod = products.merge(unit_cost_avg, on="product_id")
    prod = prod.merge(avg_monthly_qty, on="product_id")

    # Supplier por categoria
    supplier_map = (
        suppliers.groupby("category")["supplier_id"]
        .apply(list)
        .to_dict()
    )

    # Generar ordenes de compra
    rows = []
    purchase_id = 1
    date_range = pd.date_range("2014-01-01", "2017-09-01", freq="MS")

    for _, row in prod.iterrows():
        lead_time = LEAD_TIMES[row["category"]]
        suppliers_for_cat = supplier_map[row["category"]]

        for month_start in date_range:
            # Cantidad a comprar: velocidad mensual promedio con variacion ±20%
            qty = max(1, int(row["avg_monthly_qty"] * np.random.uniform(0.8, 1.2)))

            # Costo unitario con variacion ±5%
            unit_cost = round(row["avg_unit_cost"] * np.random.uniform(0.95, 1.05), 4)

            # Fecha de compra
            day = np.random.randint(1, 29)
            purchase_date = month_start + pd.Timedelta(days=day) - pd.Timedelta(days=lead_time)

            rows.append({
                "purchase_id": f"PO-{purchase_id:06d}",
                "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                "product_id": row["product_id"],
                "supplier_id": np.random.choice(suppliers_for_cat),
                "quantity": qty,
                "unit_cost": unit_cost,
                "total_cost": round(qty * unit_cost, 4)
            })
            purchase_id += 1

    return pd.DataFrame(rows)

def build_inventory(sales, purchases, products):
    date_range = pd.date_range("2014-01-01", "2017-09-01", freq="MS")

    sales["year_month"] = sales["order_date"].dt.to_period("M")
    monthly_sales = (
        sales[sales["year_month"] != pd.Period("2017-09", "M")]
        .groupby(["product_id", "year_month"])["quantity"]
        .sum()
        .rename("qty_sold")
    )

    purchases["purchase_date"] = pd.to_datetime(purchases["purchase_date"])
    purchases["year_month"] = purchases["purchase_date"].dt.to_period("M")
    monthly_purchases = (
        purchases.groupby(["product_id", "year_month"])["quantity"]
        .sum()
        .rename("qty_purchased")
    )

    daily_velocity = (
        monthly_sales.groupby("product_id")
        .mean()
        .div(30)
        .rename("daily_velocity")
    )

    lead_time_map = products.set_index("product_id")["category"].map(LEAD_TIMES)

    # Stock inicial: 2 meses de ventas promedio
    stock_state = (daily_velocity * 60).clip(lower=10).astype(int).to_dict()

    rows = []
    for month_start in date_range:
        period = month_start.to_period("M")

        for product_id in products["product_id"]:
            purchased = monthly_purchases.get((product_id, period), 0)
            sold = monthly_sales.get((product_id, period), 0)

            stock_state[product_id] = max(0, stock_state.get(product_id, 0) + purchased - sold)
            stock_qty = stock_state[product_id]

            vel = daily_velocity.get(product_id, 0.1)
            lead = lead_time_map.get(product_id, 14)

            rows.append({
                "snapshot_date": month_start.strftime("%Y-%m-%d"),
                "product_id": product_id,
                "stock_qty": stock_qty,
                "reorder_point": round(vel * lead, 2),
                "days_of_stock": round(stock_qty / vel, 1) if vel > 0 else 0
            })

    return pd.DataFrame(rows)

def save_tables(tables, conn):
    for name, df in tables.items():
        df.to_sql(name, conn, if_exists="replace", index=False)
        print(f"✓ {name}: {len(df)} filas")

def main():
    conn = sqlite3.connect(DB_PATH)
    print("Cargando tablas base...")
    sales, products = load_tables(conn)

    print("Generando suppliers...")
    suppliers = build_suppliers()

    print("Generando purchases...")
    purchases = build_purchases(sales, products, suppliers)

    print("Generando inventory...")
    inventory = build_inventory(sales, purchases, products)
    purchases = purchases.drop(columns=["year_month"], errors="ignore")

    print("Guardando en SQLite...")
    save_tables({
        "suppliers": suppliers,
        "purchases": purchases,
        "inventory": inventory
    }, conn)

    conn.close()
    print(f"\nListo. DB: {DB_PATH}")

if __name__ == "__main__":
    main()