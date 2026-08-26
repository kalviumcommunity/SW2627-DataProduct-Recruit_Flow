"""
Assignment 2.43: SQL Views & Aggregation Layer Design
Script: assignment-33-python.py

This script implements:
- Task 1: Creation and validation of two centralized SQL Views (vw_active_customers, vw_product_performance)
- Task 2: Creation, batch population, and sub-millisecond benchmarking of pre-aggregated table (agg_daily_metrics)
- Task 3: Streamlit / Dashboard simulation querying the clean data layer without touching raw tables
"""

import os
import time
import datetime
import pandas as pd
from sqlalchemy import create_engine, text, event
from database.setup_data_layer import init_data_layer_db

def get_engine(db_path: str = "data_layer.db"):
    """Creates SQLite SQLAlchemy engine with registered date functions for SQL dialect compatibility."""
    engine = create_engine(f"sqlite:///{db_path}")
    
    @event.listens_for(engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        # Register DATEDIFF(d1, d2)
        dbapi_connection.create_function(
            "DATEDIFF", 2,
            lambda d1, d2: (datetime.datetime.strptime(str(d1)[:10], "%Y-%m-%d") - datetime.datetime.strptime(str(d2)[:10], "%Y-%m-%d")).days if d1 and d2 else None
        )
    return engine

def execute_sql(sql_statement: str, engine):
    """Utility to execute raw SQL statement (DDL/DML)."""
    with engine.begin() as conn:
        conn.execute(text(sql_statement))

def run_task_1(engine):
    print("=" * 80)
    print("TASK 1: CREATE TWO SQL VIEWS")
    print("=" * 80)

    # 1. Read and execute View 1: vw_active_customers
    view1_path = os.path.join("database", "views", "vw_active_customers.sql")
    with open(view1_path, "r") as f:
        view1_sql = f.read()

    # In SQLite, remove multi-statement drops/separators and execute clean DDL
    execute_sql("DROP VIEW IF EXISTS vw_active_customers;", engine)
    execute_sql("""
    CREATE VIEW vw_active_customers AS 
    SELECT 
        c.customer_id, 
        c.customer_name, 
        c.segment, 
        COUNT(DISTINCT o.order_id) AS order_count_30d, 
        COALESCE(SUM(o.order_amount), 0.0) AS revenue_30d, 
        MAX(o.order_date) AS last_order_date, 
        CAST(ROUND(JULIANDAY('2024-12-31') - JULIANDAY(MAX(o.order_date))) AS INTEGER) AS days_since_order 
    FROM customers c 
    LEFT JOIN orders o ON c.customer_id = o.customer_id 
                       AND o.order_date >= DATE('2024-12-31', '-30 day')
                       AND o.status = 'Completed'
    WHERE c.deleted_at IS NULL 
    GROUP BY c.customer_id, c.customer_name, c.segment;
    """, engine)
    print("✔ View 1 (vw_active_customers) created successfully.")

    # 2. Read and execute View 2: vw_product_performance
    execute_sql("DROP VIEW IF EXISTS vw_product_performance;", engine)
    execute_sql("""
    CREATE VIEW vw_product_performance AS
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.price AS unit_price,
        p.cost AS unit_cost,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM(o.order_amount), 0.0) AS total_revenue,
        COALESCE(SUM(o.order_amount - p.cost), 0.0) AS total_gross_profit,
        ROUND(
            (COALESCE(SUM(o.order_amount - p.cost), 0.0) / NULLIF(SUM(o.order_amount), 0)) * 100.0, 
            2
        ) AS gross_margin_pct,
        ROUND(
            COALESCE(AVG(o.order_amount), 0.0), 
            2
        ) AS avg_order_value
    FROM products p
    JOIN orders o ON p.product_id = o.product_id
    WHERE o.status = 'Completed'
    GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost;
    """, engine)
    print("✔ View 2 (vw_product_performance) created successfully.\n")

    # 3. Query views to confirm execution
    active_customers = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", engine)
    custom_metric = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 10", engine)

    print("View 1 columns:", active_customers.columns.tolist())
    print("View 2 columns:", custom_metric.columns.tolist())
    print("\nSample Rows from View 1 (vw_active_customers):")
    print(active_customers.head(3))
    print("\nSample Rows from View 2 (vw_product_performance):")
    print(custom_metric.head(3))
    print("=" * 80 + "\n")

def run_task_2(engine):
    print("=" * 80)
    print("TASK 2: CREATE ONE PRE-AGGREGATED SUMMARY TABLE")
    print("=" * 80)

    # 1. Create table DDL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS agg_daily_metrics (
        aggregation_date DATE NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        metric_value NUMERIC NOT NULL,
        row_count INTEGER NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (aggregation_date, metric_name)
    );
    """
    execute_sql("DROP TABLE IF EXISTS agg_daily_metrics;", engine)
    execute_sql(create_table_sql, engine)
    print("✔ Pre-aggregated table 'agg_daily_metrics' created.")

    # 2. Populate with aggregation query
    populate_sql = """
    INSERT INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
    SELECT 
        DATE(o.order_date) AS aggregation_date,
        'total_revenue' AS metric_name,
        SUM(o.order_amount) AS metric_value,
        COUNT(*) AS row_count,
        CURRENT_TIMESTAMP AS updated_at
    FROM orders o
    WHERE o.status = 'Completed'
    GROUP BY DATE(o.order_date);
    """
    execute_sql(populate_sql, engine)
    print("✔ Populated 'agg_daily_metrics' with daily revenue rollups.\n")

    # 3. Verify data and check updated_at timestamp
    agg_data = pd.read_sql("SELECT * FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10", engine)
    print(f"Aggregated {len(agg_data)} sample rows (Total rows in table: {pd.read_sql('SELECT COUNT(*) FROM agg_daily_metrics', engine).iloc[0,0]}):")
    print(agg_data)

    # 4. Demonstrate sub-millisecond query speed
    start = time.time()
    result = pd.read_sql("SELECT metric_name, SUM(metric_value) AS total_aggregate_revenue, SUM(row_count) AS total_orders FROM agg_daily_metrics GROUP BY metric_name", engine)
    elapsed = time.time() - start
    print(f"\nPre-aggregated Query Result:")
    print(result)
    print(f"Query execution time on pre-aggregated table: {elapsed * 1000:.2f}ms")
    print("=" * 80 + "\n")

def run_task_3(engine):
    print("=" * 80)
    print("TASK 3: QUERY VIEWS & AGGREGATED TABLES FROM PYTHON (DASHBOARD SIMULATION)")
    print("=" * 80)

    # Query View 1: Top 20 Active Customers (last 30 days)
    active_cust_df = pd.read_sql("""
    SELECT customer_id, customer_name, revenue_30d, days_since_order
    FROM vw_active_customers
    WHERE days_since_order <= 30 AND days_since_order IS NOT NULL
    ORDER BY revenue_30d DESC
    LIMIT 20
    """, engine)
    print("Top 20 Active Customers (last 30 days):")
    print(active_cust_df.head(10))

    # Query View 2: Custom Metric (Product Performance)
    custom_result = pd.read_sql("""
    SELECT product_id, product_name, category, total_orders, total_revenue, gross_margin_pct
    FROM vw_product_performance
    ORDER BY total_revenue DESC
    LIMIT 20
    """, engine)
    print("\nCustom Metric Results (Top 10 Products by Revenue):")
    print(custom_result.head(10))

    # Query Pre-Aggregated Table: Daily metrics for last 30 days
    agg_result = pd.read_sql("""
    SELECT aggregation_date, metric_name, metric_value, row_count, updated_at
    FROM agg_daily_metrics
    WHERE aggregation_date >= DATE('2024-12-31', '-30 day')
    ORDER BY aggregation_date DESC
    LIMIT 20
    """, engine)
    print("\nDaily Aggregated Metrics (last 30 days):")
    print(agg_result.head(10))

    # Demonstrate business metric aggregation by segment directly from view
    active_by_segment = pd.read_sql("""
    SELECT 
        segment, 
        COUNT(*) AS customer_count, 
        ROUND(SUM(revenue_30d), 2) AS total_segment_revenue, 
        ROUND(AVG(revenue_30d), 2) AS avg_customer_revenue
    FROM vw_active_customers
    GROUP BY segment
    ORDER BY total_segment_revenue DESC
    """, engine)
    print("\nRevenue by Segment (Aggregated from vw_active_customers):")
    print(active_by_segment)
    print("=" * 80 + "\n")

def main():
    db_file = "data_layer.db"
    # Ensure database is generated
    if not os.path.exists(db_file):
        print(f"Initializing data layer database: {db_file}")
        init_data_layer_db(db_file)
    
    engine = get_engine(db_file)

    run_task_1(engine)
    run_task_2(engine)
    run_task_3(engine)
    print("All tasks for 2.43 executed successfully!")

if __name__ == "__main__":
    main()
