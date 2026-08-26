"""
Database setup script for SQL Views & Aggregation Layer Design (2.43).
Creates customers, products, and orders tables with realistic analytical test data.
"""

import sqlite3
import random
import datetime

def init_data_layer_db(db_path: str = "data_layer.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP VIEW IF EXISTS vw_active_customers;")
    cursor.execute("DROP VIEW IF EXISTS vw_product_performance;")
    cursor.execute("DROP TABLE IF EXISTS agg_daily_metrics;")
    cursor.execute("DROP TABLE IF EXISTS orders;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    cursor.execute("DROP TABLE IF EXISTS products;")

    # 1. Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        email TEXT,
        segment TEXT NOT NULL,
        country TEXT NOT NULL,
        created_at TEXT NOT NULL,
        deleted_at TEXT
    );
    """)

    # 2. Create products table
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        cost REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 3. Create orders table
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        order_amount REAL NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    random.seed(42)

    # Populate Customers (500 customers)
    segments = ["Enterprise", "Mid-Market", "SMB", "Consumer", "VIP"]
    countries = ["USA", "Canada", "UK", "Germany", "France", "Australia", "India", "Japan"]
    
    customers_data = []
    for c_id in range(1, 501):
        c_name = f"Customer_{c_id}"
        email = f"customer_{c_id}@example.com"
        seg = random.choice(segments)
        country = random.choice(countries)
        created = "2023-01-15"
        # 5% soft deleted
        deleted = "2024-06-01" if random.random() < 0.05 else None
        customers_data.append((c_id, c_name, email, seg, country, created, deleted))

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?);", customers_data)

    # Populate Products (50 products)
    categories = ["Cloud Infrastructure", "Developer Tools", "AI & ML Services", "Security", "Analytics Suite"]
    products_data = []
    for p_id in range(1, 51):
        p_name = f"Product_{p_id}"
        cat = random.choice(categories)
        price = round(random.uniform(50.0, 2000.0), 2)
        cost = round(price * random.uniform(0.3, 0.65), 2)
        created = "2023-01-01"
        products_data.append((p_id, p_name, cat, price, cost, created))

    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?);", products_data)

    # Populate Orders (15,000 orders across 2024)
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    date_days = (end_date - start_date).days

    orders_data = []
    for o_id in range(1, 15001):
        c_id = random.randint(1, 500)
        p_id = random.randint(1, 50)
        # Fetch base product price for realistic variance
        base_price = products_data[p_id - 1][3]
        qty = random.randint(1, 5)
        amt = round(base_price * qty * random.uniform(0.9, 1.1), 2)
        o_date = (start_date + datetime.timedelta(days=random.randint(0, date_days))).isoformat()
        st = "Completed" if random.random() > 0.1 else random.choice(["Cancelled", "Refunded"])
        created = f"{o_date} 10:00:00"
        orders_data.append((o_id, c_id, p_id, amt, o_date, st, created))

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?);", orders_data)

    conn.commit()
    conn.close()
    print(f"Data layer database initialized at {db_path} with:")
    print(f" - 500 customers")
    print(f" - 50 products")
    print(f" - 15,000 orders")

if __name__ == "__main__":
    init_data_layer_db("data_layer.db")
