"""
Task 2: Refactor Query 2 - Apply Filters Before JOINs

Performance Improvement Docstring:
-----------------------------------
In unoptimized SQL queries, tables are frequently joined in full before WHERE filter conditions
are evaluated. When joining massive tables (e.g. 100M transactions to 10M customers and products),
joining first forces the database query engine to construct massive Cartesian/hash-join intermediate 
structures in memory or spill them to temporary disk space, only to discard 90%+ of the joined rows 
during post-join predicate evaluation.

By filtering BEFORE joining (via Predicate Pushdown, Subqueries, or filtered CTEs):
1. Intermediate Dataset Minimization: The join cardinality is reduced by the filter selectivity ratio
   (e.g., 2x to 10x+ fewer rows entering the hash/merge join phase).
2. Memory & CPU Efficiency: Hash tables built for join lookups are orders of magnitude smaller, fitting
   neatly into CPU L3 cache or RAM rather than spilling to disk.
3. Compounding Speedup: Filtering early on indexed date/amount predicates drastically cuts compute time.
"""

import time
import pandas as pd
from sqlalchemy import create_engine

def get_db_engine(db_path: str = "analytics.db"):
    return create_engine(f"sqlite:///{db_path}")

def run_task_2():
    engine = get_db_engine()

    print("=" * 80)
    print("TASK 2: REFACTOR QUERY 2 - APPLY FILTERS BEFORE JOINS")
    print("=" * 80)

    # 1. Measure raw baseline transaction table row count
    transactions_count = pd.read_sql("SELECT COUNT(*) FROM transactions", engine).iloc[0, 0]

    # 2. Original Inefficient Query (Joins entire tables before filtering)
    inefficient_query = """
    SELECT 
        t.transaction_id, 
        t.amount, 
        c.customer_name, 
        p.product_name 
    FROM transactions t 
    JOIN customers c ON t.customer_id = c.id 
    JOIN products p ON t.product_id = p.id 
    WHERE t.transaction_date >= '2024-01-01' 
      AND t.amount > 100 
      AND c.country = 'USA' 
    LIMIT 5000;
    """

    start_time = time.perf_counter()
    result_inefficient = pd.read_sql(inefficient_query, engine)
    inefficient_time_ms = (time.perf_counter() - start_time) * 1000

    # 3. Measure filtered transactions count before join
    filtered_transactions = pd.read_sql("""
    SELECT COUNT(*) 
    FROM transactions 
    WHERE transaction_date >= '2024-01-01' 
      AND amount > 100;
    """, engine).iloc[0, 0]

    # 4. Efficient Query: Filter transactions in CTE before joining customers and products
    # Note: We also select only required columns (transaction_id, customer_id, product_id, amount) inside the CTE
    efficient_query = """
    WITH filtered_trans AS (
        -- Filter early: Reduce 30,000 rows down before performing 2 table joins
        SELECT 
            transaction_id, 
            customer_id, 
            product_id, 
            amount 
        FROM transactions 
        WHERE transaction_date >= '2024-01-01' 
          AND amount > 100
    ) 
    SELECT 
        ft.transaction_id, 
        ft.amount, 
        c.customer_name, 
        p.product_name 
    FROM filtered_trans ft 
    JOIN customers c ON ft.customer_id = c.id 
    JOIN products p ON ft.product_id = p.id 
    WHERE c.country = 'USA' 
    LIMIT 5000;
    """

    start_time = time.perf_counter()
    result_efficient = pd.read_sql(efficient_query, engine)
    efficient_time_ms = (time.perf_counter() - start_time) * 1000

    # Validation: Both queries return identical records
    pd.testing.assert_frame_equal(
        result_inefficient.sort_values(by="transaction_id").reset_index(drop=True),
        result_efficient.sort_values(by="transaction_id").reset_index(drop=True),
        check_dtype=False
    )
    print("✔ Validation Passed: Both inefficient and efficient queries return identical results.\n")

    # Metrics and Reduction Factor Calculations
    reduction_pct = (filtered_transactions / transactions_count) * 100
    reduction_factor = transactions_count / filtered_transactions if filtered_transactions > 0 else 1.0

    print(f"Original table:             {transactions_count:,} rows")
    print(f"After filter (before join): {filtered_transactions:,} rows ({reduction_pct:.1f}% of total table)")
    print(f"Final joined result:        {len(result_efficient):,} rows")
    print(f"Reduction factor:           {reduction_factor:.2f}x smaller dataset before joining\n")

    print(f"Inefficient Query Time:     {inefficient_time_ms:.2f} ms")
    print(f"Efficient Query Time:       {efficient_time_ms:.2f} ms")
    print("\nSample Output (First 5 Rows):")
    print(result_efficient.head())
    print("=" * 80 + "\n")

    return {
        "transactions_count": transactions_count,
        "filtered_transactions": filtered_transactions,
        "final_rows": len(result_efficient),
        "reduction_factor": reduction_factor,
        "inefficient_time_ms": inefficient_time_ms,
        "efficient_time_ms": efficient_time_ms
    }

if __name__ == "__main__":
    run_task_2()
