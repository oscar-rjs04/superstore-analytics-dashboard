import os
import sqlite3

import pandas as pd

DB_PATH = "database/superstore.db"
EXPORT_PATH = "data/processed"

def export_all():
    os.makedirs(EXPORT_PATH, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    tables = ["customers", "products", "locations", "dates", 
              "sales", "suppliers", "purchases", "inventory"]
    print("Exportando tablas a CSV...")
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        path = f"{EXPORT_PATH}/{table}.csv"
        df.to_csv(path, index=False)
        print(f"✓ {table} → {path}")
    
    conn.close()

if __name__ == "__main__":
    export_all()