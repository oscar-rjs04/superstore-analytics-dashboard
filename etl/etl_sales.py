import os
import sqlite3

import pandas as pd

RAW_PATH = "data/raw/Superstore.csv"
DB_PATH = "database/superstore.db"

def load_raw(path):
    df = pd.read_csv(path, encoding="latin-1")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df = df.drop(columns=['Row ID','Country'])
    return df

def build_customers(df):
    return(
        df[['Customer ID', 'Customer Name', 'Segment']]
        .drop_duplicates(subset='Customer ID')
        .rename(columns={
            'Customer ID': 'customer_id', 
            'Customer Name': 'customer_name', 
            'Segment': 'segment'
        })
        .reset_index(drop=True)
    )

def build_products(df):
    return(
        df[['Product ID', 'Category', 'Sub-Category']]
        .drop_duplicates(subset='Product ID')
        .rename(columns={
            'Product ID': 'product_id', 
            'Category': 'category', 
            'Sub-Category': 'sub_category'
        })
        .reset_index(drop=True)
    )

def build_locations(df):
    return(
        df[['Postal Code', 'City', 'State', 'Region']]
        .drop_duplicates(subset='Postal Code')  # mantiene el primero
        .rename(columns={
            'Postal Code': 'postal_code',
            'City': 'city', 
            'State': 'state', 
            'Region': 'region'
        })
        .reset_index(drop=True)
    )

def build_dates(df):
    all_dates = pd.concat([df['Order Date'], df['Ship Date']]).drop_duplicates()
    dates = pd.DataFrame({'date': all_dates}).sort_values('date').reset_index(drop=True)
    dates['year'] = dates['date'].dt.year
    dates['quarter'] = dates['date'].dt.quarter
    dates['month'] = dates['date'].dt.month
    dates['month_name'] = dates['date'].dt.strftime('%B')
    dates['week'] = dates['date'].dt.isocalendar().week.astype(int)
    dates['date'] = dates['date'].dt.strftime('%Y-%m-%d')
    return dates

def build_sales(df):
    sales = df.rename(columns={
        'Order ID': 'order_id',
        'Order Date': 'order_date',
        'Ship Date': 'ship_date',
        'Ship Mode': 'ship_mode',
        'Customer ID': 'customer_id',
        'Product ID': 'product_id',
        'Postal Code': 'postal_code',
        'Sales': 'sales',
        'Quantity': 'quantity',
        'Discount': 'discount',
        'Profit': 'profit'
    })[[
        'order_id', 'order_date', 'ship_date', 'ship_mode', 
        'customer_id', 'product_id', 'postal_code', 
        'sales', 'quantity', 'discount', 'profit'
    ]].copy()

    sales['cost'] = sales['sales'] - sales['profit']
    sales['order_date'] = pd.to_datetime(sales['order_date']).dt.strftime('%Y-%m-%d')
    sales['ship_date'] = pd.to_datetime(sales['ship_date']).dt.strftime('%Y-%m-%d')
    return sales

def save_to_sqlite(tables: dict, db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    for table_name, df in tables.items():
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"\nBase de datos guardada en: {db_path}")

def main():
    print("Cargando datos...")
    df = load_raw(RAW_PATH)

    print("Construyendo tablas...")
    tables = {
        'customers': build_customers(df),
        'products': build_products(df),
        'locations': build_locations(df),
        'dates': build_dates(df),
        'sales': build_sales(df)
    }

    save_to_sqlite(tables, DB_PATH)

if __name__ == "__main__":
    main()