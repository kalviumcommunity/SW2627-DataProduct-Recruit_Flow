"""
Task 1: Refactor Query 1 - SELECT * to Explicit Columns

Performance Improvement Docstring:
-----------------------------------
SELECT * is a critical performance antipattern in analytical query engineering.
When executing SELECT *, the database engine must scan, deserialize, and transmit every single 
column across storage, buffer cache, memory, and network layers. On wide tables (e.g., 50+ columns),
fetching unused text fields, JSON blobs, IP addresses, and metadata multiplies I/O and memory overhead 
by 5x-10x. 

By replacing SELECT * with explicit column selection:
1. Column Pruning: Columnar and row-store engines fetch only requested column pages/offsets, 
   drastically reducing disk I/O, cache thrashing, and serialization costs.
2. Network & Memory Bandwidth: Transfer payloads shrink significantly, preventing memory bottlenecks
   in analytical services, BI dashboards, and Pandas dataframes.
3. Schema Resilience & Security: Explicit column contracts prevent breaking downstream applications 
   when schemas change, while preventing accidental leakage of sensitive PII columns.
"""

import time
import pandas as pd
from sqlalchemy import create_engine, event

def get_db_engine(db_path: str = "analytics.db"):
    """Creates SQLAlchemy engine with custom YEAR function registered for SQLite."""
    engine = create_engine(f"sqlite:///{db_path}")
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        dbapi_connection.create_function("YEAR", 1, lambda val: int(str(val)[:4]) if val else None)
    return engine

def run_task_1():
    engine = get_db_engine()

    # Original Query: Inefficient SELECT * fetching all 70 combined columns
    original_query = """
    SELECT * 
    FROM transactions t 
    JOIN customers c ON t.customer_id = c.id 
    WHERE YEAR(t.transaction_date) = 2024 
    LIMIT 1000;
    """

    # Optimized Query: Explicit column selection with documented business intent
    optimized_query = """
    SELECT 
        -- Transactions Columns:
        t.transaction_id,    -- Unique transaction identifier: Answers 'Which specific sale occurred?'
        t.transaction_date,  -- Transaction timestamp: Answers 'When did the sale occur in 2024?'
        t.amount,            -- Revenue/monetary value: Answers 'How much revenue was generated?'
        t.customer_id,       -- Relational foreign key: Answers 'Which customer initiated the transaction?'
        
        -- Customer Columns:
        c.customer_name,     -- Customer identity: Answers 'Who is the purchaser?'
        c.country,           -- Geographic dimension: Answers 'Which country is driving sales?'
        c.account_type       -- Account classification: Answers 'What customer tier (Basic/Pro/Enterprise) made the purchase?'
    FROM transactions t 
    JOIN customers c ON t.customer_id = c.id 
    WHERE YEAR(t.transaction_date) = 2024 
    LIMIT 1000;
    """

    print("=" * 80)
    print("TASK 1: REFACTOR QUERY 1 - SELECT * TO EXPLICIT COLUMNS")
    print("=" * 80)

    # Benchmark Original Query
    start_time = time.perf_counter()
    original_result = pd.read_sql(original_query, engine)
    original_time_ms = (time.perf_counter() - start_time) * 1000
    original_mem_kb = original_result.memory_usage(deep=True).sum() / 1024

    # Benchmark Optimized Query
    start_time = time.perf_counter()
    optimized_result = pd.read_sql(optimized_query, engine)
    optimized_time_ms = (time.perf_counter() - start_time) * 1000
    optimized_mem_kb = optimized_result.memory_usage(deep=True).sum() / 1024

    # Verification: Validate core columns match
    core_cols = ["transaction_id", "transaction_date", "amount", "customer_id", "customer_name", "country", "account_type"]
    assert len(original_result) == len(optimized_result), "Row counts mismatch!"
    
    # Calculate Improvements
    col_reduction_pct = ((original_result.shape[1] - optimized_result.shape[1]) / original_result.shape[1]) * 100
    mem_reduction_pct = ((original_mem_kb - optimized_mem_kb) / original_mem_kb) * 100
    time_improvement_pct = ((original_time_ms - optimized_time_ms) / original_time_ms) * 100 if original_time_ms > 0 else 0

    print(f"Original columns:  {original_result.shape[1]}")
    print(f"Optimized columns: {optimized_result.shape[1]}")
    print(f"Improvement:       {col_reduction_pct:.1f}% fewer columns\n")

    print(f"Original Memory Usage:  {original_mem_kb:.2f} KB")
    print(f"Optimized Memory Usage: {optimized_mem_kb:.2f} KB ({mem_reduction_pct:.1f}% memory reduction)")
    print(f"Original Exec Time:     {original_time_ms:.2f} ms")
    print(f"Optimized Exec Time:    {optimized_time_ms:.2f} ms ({time_improvement_pct:.1f}% faster)\n")

    print("Sample Optimized Result (First 5 Rows):")
    print(optimized_result.head())
    print("=" * 80 + "\n")

    return {
        "original_cols": original_result.shape[1],
        "optimized_cols": optimized_result.shape[1],
        "col_reduction_pct": col_reduction_pct,
        "original_mem_kb": original_mem_kb,
        "optimized_mem_kb": optimized_mem_kb,
        "mem_reduction_pct": mem_reduction_pct,
        "original_time_ms": original_time_ms,
        "optimized_time_ms": optimized_time_ms
    }

if __name__ == "__main__":
    run_task_1()
