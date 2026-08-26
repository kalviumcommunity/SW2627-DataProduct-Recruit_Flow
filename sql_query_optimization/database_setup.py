"""
Database setup script for Analytical SQL Query Optimization.
Generates synthetic data for transactions (50+ columns), customers, and products tables
to simulate a realistic production analytical warehouse environment.
"""

import sqlite3
import random
import datetime
import pandas as pd
from sqlalchemy import create_engine, text

def create_and_populate_database(db_path: str = "analytics.db", num_transactions: int = 50000, num_customers: int = 2000, num_products: int = 200):
    """
    Creates SQLite database and populates it with realistic analytical tables.
    Includes custom SQLite scalar functions such as YEAR() for SQL standard compatibility.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if present
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    cursor.execute("DROP TABLE IF EXISTS products;")

    # 1. Create customers table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        email TEXT,
        country TEXT NOT NULL,
        account_type TEXT NOT NULL,
        customer_segment TEXT NOT NULL,
        loyalty_tier TEXT,
        signup_date TEXT,
        lifetime_value REAL,
        industry TEXT,
        company_size TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        postal_code TEXT,
        is_active INTEGER,
        churn_risk REAL,
        preferred_currency TEXT,
        support_tier TEXT,
        notes TEXT
    );
    """)

    # 2. Create products table
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        cost REAL NOT NULL,
        sku TEXT UNIQUE,
        manufacturer TEXT,
        weight_kg REAL,
        dimensions TEXT,
        is_in_stock INTEGER,
        stock_quantity INTEGER,
        supplier_id INTEGER,
        created_at TEXT,
        updated_at TEXT,
        description TEXT
    );
    """)

    # 3. Create transactions table with 50 columns to demonstrate SELECT * overhead
    cursor.execute("""
    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY,
        transaction_date TEXT NOT NULL,
        amount REAL NOT NULL,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        discount REAL,
        tax REAL,
        payment_method TEXT,
        currency TEXT,
        status TEXT,
        ip_address TEXT,
        device_type TEXT,
        user_agent TEXT,
        billing_address_line1 TEXT,
        billing_address_line2 TEXT,
        billing_city TEXT,
        billing_state TEXT,
        billing_postal_code TEXT,
        billing_country TEXT,
        shipping_address_line1 TEXT,
        shipping_address_line2 TEXT,
        shipping_city TEXT,
        shipping_state TEXT,
        shipping_postal_code TEXT,
        shipping_country TEXT,
        merchant_id TEXT,
        terminal_id TEXT,
        session_id TEXT,
        referral_code TEXT,
        coupon_id TEXT,
        fulfillment_status TEXT,
        tracking_number TEXT,
        notes TEXT,
        metadata_json TEXT,
        risk_score REAL,
        authorization_code TEXT,
        gateway_response TEXT,
        created_at TEXT,
        updated_at TEXT,
        is_flagged INTEGER,
        fraud_check_status TEXT,
        batch_id TEXT,
        settled_at TEXT,
        fee_amount REAL,
        net_amount REAL,
        channel TEXT,
        loyalty_points_earned INTEGER,
        loyalty_points_redeemed INTEGER,
        refund_status TEXT,
        external_reference TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # Seed for deterministic generation
    random.seed(42)

    countries = ["USA", "USA", "USA", "Canada", "UK", "Germany", "France", "Australia", "India", "Japan"]
    account_types = ["Standard", "Premium", "Enterprise", "Basic", "Pro"]
    segments = ["Enterprise", "Mid-Market", "SMB", "Consumer", "VIP"]
    categories = ["Hardware", "Software", "Cloud Services", "Consulting", "Support", "Peripherals"]
    devices = ["Desktop", "Mobile", "Tablet", "API", "POS"]
    channels = ["Web", "Mobile App", "In-Store", "Partner API", "Phone"]
    statuses = ["Completed", "Completed", "Completed", "Pending", "Failed", "Refunded"]

    # Generate Customers
    customers_data = []
    for c_id in range(1, num_customers + 1):
        c_name = f"Customer_{c_id}"
        email = f"user{c_id}@company{c_id % 50}.com"
        country = random.choice(countries)
        acc_type = random.choice(account_types)
        segment = random.choice(segments)
        tier = random.choice(["Bronze", "Silver", "Gold", "Platinum"])
        signup = f"202{random.randint(1, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        ltv = round(random.uniform(500, 50000), 2)
        ind = random.choice(["Technology", "Healthcare", "Finance", "Retail", "Manufacturing"])
        size = random.choice(["1-10", "11-50", "51-200", "201-1000", "1000+"])
        customers_data.append((
            c_id, c_name, email, country, acc_type, segment, tier, signup, ltv, ind, size,
            f"{c_id} Main St", "Cityville", "State", "12345", 1, round(random.uniform(0.01, 0.40), 3),
            "USD", "Tier 1", "Standard customer account"
        ))

    cursor.executemany("""
    INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, customers_data)

    # Generate Products
    products_data = []
    for p_id in range(1, num_products + 1):
        p_name = f"Product_{p_id}"
        cat = random.choice(categories)
        price = round(random.uniform(20.0, 1500.0), 2)
        cost = round(price * random.uniform(0.3, 0.7), 2)
        sku = f"SKU-{p_id:05d}"
        mfg = f"Manufacturer {p_id % 10 + 1}"
        wt = round(random.uniform(0.1, 25.0), 2)
        dim = f"{random.randint(5, 50)}x{random.randint(5, 50)}x{random.randint(5, 50)} cm"
        instock = 1 if random.random() > 0.1 else 0
        qty = random.randint(0, 500)
        sup_id = random.randint(1, 20)
        created = "2023-01-01"
        updated = "2024-01-01"
        desc = f"High performance {cat.lower()} solution for enterprise workflows."
        products_data.append((
            p_id, p_name, cat, price, cost, sku, mfg, wt, dim, instock, qty, sup_id, created, updated, desc
        ))

    cursor.executemany("""
    INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, products_data)

    # Generate Transactions
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2024, 12, 31)
    date_range_days = (end_date - start_date).days

    transactions_data = []
    for t_id in range(1, num_transactions + 1):
        rand_days = random.randint(0, date_range_days)
        t_date = (start_date + datetime.timedelta(days=rand_days)).isoformat()
        amt = round(random.uniform(10.0, 2500.0), 2)
        c_id = random.randint(1, num_customers)
        p_id = random.randint(1, num_products)
        disc = round(amt * random.choice([0.0, 0.05, 0.10, 0.15]), 2)
        tax = round((amt - disc) * 0.08, 2)
        pm = random.choice(["Credit Card", "Wire Transfer", "ACH", "PayPal", "Corporate Card"])
        curr = "USD"
        st = random.choice(statuses)
        ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        dev = random.choice(devices)
        ua = f"Mozilla/5.0 (AnalyticsAgent/{random.randint(1, 10)}.0)"
        b_addr1 = f"{random.randint(100, 9999)} Commerce Way"
        b_addr2 = f"Suite {random.randint(100, 900)}"
        b_city = "Metropolis"
        b_state = "NY"
        b_zip = "10001"
        b_country = "USA"
        s_addr1 = b_addr1
        s_addr2 = b_addr2
        s_city = b_city
        s_state = b_state
        s_zip = b_zip
        s_country = b_country
        m_id = f"MID-{random.randint(1000, 9999)}"
        term_id = f"TERM-{random.randint(100, 999)}"
        sess_id = f"SESS-{random.randint(100000, 999999)}"
        ref = f"REF-{random.randint(100, 999)}" if random.random() > 0.7 else None
        coupon = f"SAVE{random.choice([10, 20, 30])}" if random.random() > 0.8 else None
        ful_st = "Delivered" if st == "Completed" else "Processing"
        trk = f"1Z{random.randint(10000000, 99999999)}"
        notes = "Processed through primary analytical gateway."
        meta_json = f'{{"session": "{sess_id}", "retries": 0, "verified": true}}'
        risk = round(random.uniform(0.01, 0.99), 2)
        auth_code = f"AUTH{random.randint(100000, 999999)}"
        gw_resp = "200_OK_APPROVED"
        created = f"{t_date} 12:00:00"
        updated = created
        flagged = 1 if risk > 0.85 else 0
        fraud_st = "PASS" if not flagged else "REVIEW"
        batch = f"BATCH-{t_date[:7]}"
        settled = f"{t_date} 23:59:59"
        fee = round(amt * 0.025 + 0.30, 2)
        net = round(amt - disc - fee, 2)
        chan = random.choice(channels)
        pts_earned = int(amt // 10)
        pts_redeemed = 0 if random.random() > 0.2 else random.randint(10, 100)
        ref_st = "NONE" if st != "Refunded" else "FULL"
        ext_ref = f"EXT-{t_id:08d}"

        transactions_data.append((
            t_id, t_date, amt, c_id, p_id, disc, tax, pm, curr, st,
            ip, dev, ua, b_addr1, b_addr2, b_city, b_state, b_zip, b_country,
            s_addr1, s_addr2, s_city, s_state, s_zip, s_country,
            m_id, term_id, sess_id, ref, coupon, ful_st, trk, notes, meta_json,
            risk, auth_code, gw_resp, created, updated, flagged, fraud_st, batch,
            settled, fee, net, chan, pts_earned, pts_redeemed, ref_st, ext_ref
        ))

    cursor.executemany("""
    INSERT INTO transactions VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    );
    """, transactions_data)

    conn.commit()
    conn.close()
    print(f"Database created at {db_path} with:")
    print(f" - {num_customers} customers")
    print(f" - {num_products} products")
    print(f" - {num_transactions} transactions (50 columns each)")

def get_engine(db_path: str = "analytics.db"):
    """
    Returns SQLAlchemy engine connected to SQLite with YEAR() function registered.
    """
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Register YEAR() SQLite custom function for SQL dialect compatibility
    @sqlite3.connect
    def _dummy():
        pass

    with engine.connect() as connection:
        raw_conn = connection.connection.dbapi_connection
        raw_conn.create_function("YEAR", 1, lambda val: int(str(val)[:4]) if val else None)
        
    return engine

if __name__ == "__main__":
    create_and_populate_database("analytics.db", num_transactions=30000, num_customers=1000, num_products=100)
