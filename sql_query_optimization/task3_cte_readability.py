"""
Task 3: Refactor Query 3 - Use CTEs for Readability and Maintainability

Performance & Architectural Docstring:
---------------------------------------
Deeply nested subqueries ("SQL spaghetti") present severe engineering challenges:
1. Cognitive Load: Analytical logic is inverted; developers must read from the deepest inner subquery 
   outward to understand business transformations.
2. Inability to Unit-Test: Intermediate steps cannot be isolated or validated independently without 
   dissecting and rebuilding the query.
3. Code Duplication & Inefficiency: If the same intermediate computation is needed across multiple branches 
   (e.g., in a union or multi-join), nested subqueries force redundant execution.
4. Error-Prone Nesting: Complex subqueries often lead to redundant wrapping layers and aggregation bugs.

By restructuring with Common Table Expressions (CTEs):
1. Top-to-Bottom Storytelling: Queries follow declarative, chronological data-flow pipelines.
2. Modular Isolation: Every step has clear boundaries and can be independently verified.
3. Optimizer Reusability: Modern SQL engines can cache/materialize CTE results when referenced multiple times.
"""

import time
import pandas as pd
from sqlalchemy import create_engine

def get_db_engine(db_path: str = "analytics.db"):
    return create_engine(f"sqlite:///{db_path}")

def test_intermediate_ctes(engine):
    """Demonstrates how CTEs allow independent testing and validation of each transformation stage."""
    print("--- Independent CTE Verification Tests ---")
    
    # Test Step 1: Verify recent_transactions filter
    step1_query = """
    SELECT COUNT(*) as count_recent, MIN(transaction_date) as min_date, MAX(transaction_date) as max_date
    FROM transactions 
    WHERE transaction_date >= '2024-01-01';
    """
    s1_res = pd.read_sql(step1_query, engine)
    print(f"Step 1 (recent_transactions): {s1_res['count_recent'].iloc[0]} rows, Date Range: {s1_res['min_date'].iloc[0]} to {s1_res['max_date'].iloc[0]}")
    assert s1_res['count_recent'].iloc[0] > 0, "Step 1 returned 0 rows!"

    # Test Step 2: Verify customer_with_segment join integrity
    step2_query = """
    WITH recent_transactions AS (
        SELECT transaction_id, amount, customer_id 
        FROM transactions 
        WHERE transaction_date >= '2024-01-01'
    )
    SELECT COUNT(*) as joined_count, COUNT(customer_segment) as non_null_segments
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id;
    """
    s2_res = pd.read_sql(step2_query, engine)
    print(f"Step 2 (customer_with_segment): {s2_res['joined_count'].iloc[0]} rows matched, {s2_res['non_null_segments'].iloc[0]} valid segments")
    assert s2_res['joined_count'].iloc[0] == s2_res['non_null_segments'].iloc[0], "Customer segment missing on join!"

    # Test Step 3: Verify segment_metrics aggregation
    step3_query = """
    WITH recent_transactions AS (
        SELECT transaction_id, amount, customer_id 
        FROM transactions 
        WHERE transaction_date >= '2024-01-01'
    ),
    customer_with_segment AS (
        SELECT rt.transaction_id, rt.amount, c.customer_segment 
        FROM recent_transactions rt 
        JOIN customers c ON rt.customer_id = c.id
    )
    SELECT 
        customer_segment, 
        COUNT(DISTINCT transaction_id) as transaction_count, 
        AVG(amount) as avg_transaction_value, 
        SUM(amount) as total_revenue 
    FROM customer_with_segment 
    GROUP BY customer_segment;
    """
    s3_res = pd.read_sql(step3_query, engine)
    print(f"Step 3 (segment_metrics): Calculated metrics for {len(s3_res)} distinct customer segments.")

    print("✔ All intermediate CTE components passed individual unit tests.\n")

def run_task_3():
    engine = get_db_engine()

    print("=" * 80)
    print("TASK 3: REFACTOR QUERY 3 - USE CTES FOR READABILITY & TESTABILITY")
    print("=" * 80)

    # 1. Original Nested Subquery (Spaghetti structure with 3 levels of nesting)
    original_query = """
    SELECT 
        customer_segment, 
        revenue_per_transaction as avg_transaction_value,
        transaction_count,
        total_revenue
    FROM ( 
        SELECT 
            c.customer_segment, 
            AVG(t.amount) as revenue_per_transaction, 
            COUNT(DISTINCT t.transaction_id) as transaction_count,
            SUM(t.amount) as total_revenue
        FROM ( 
            SELECT t.transaction_id, t.amount, t.customer_id 
            FROM transactions t 
            WHERE t.transaction_date >= '2024-01-01' 
        ) t 
        JOIN customers c ON t.customer_id = c.id 
        GROUP BY c.customer_segment 
    ) grouped 
    ORDER BY avg_transaction_value DESC;
    """

    # 2. Refactored Modular CTE Query (Linear, top-to-bottom declarative pipeline)
    refactored_query = """
    WITH recent_transactions AS ( 
        -- Step 1: Filter to recent 2024+ transactions and select only required columns
        SELECT 
            transaction_id, 
            amount, 
            customer_id 
        FROM transactions 
        WHERE transaction_date >= '2024-01-01' 
    ), 
    customer_with_segment AS ( 
        -- Step 2: Join filtered transactions to customer dimension table to attach customer_segment
        SELECT 
            rt.transaction_id, 
            rt.amount, 
            c.customer_segment 
        FROM recent_transactions rt 
        JOIN customers c ON rt.customer_id = c.id 
    ), 
    segment_metrics AS ( 
        -- Step 3: Calculate segment-level aggregation metrics
        SELECT 
            customer_segment, 
            COUNT(DISTINCT transaction_id) as transaction_count, 
            AVG(amount) as avg_transaction_value, 
            SUM(amount) as total_revenue 
        FROM customer_with_segment 
        GROUP BY customer_segment 
    ) 
    -- Step 4: Final output presentation layer ordered by avg_transaction_value
    SELECT 
        customer_segment, 
        avg_transaction_value, 
        transaction_count, 
        total_revenue 
    FROM segment_metrics 
    ORDER BY avg_transaction_value DESC;
    """

    # Run independent step tests
    test_intermediate_ctes(engine)

    # Benchmark Original Nested Query
    start_time = time.perf_counter()
    original_result = pd.read_sql(original_query, engine)
    original_time_ms = (time.perf_counter() - start_time) * 1000

    # Benchmark Refactored CTE Query
    start_time = time.perf_counter()
    refactored_result = pd.read_sql(refactored_query, engine)
    refactored_time_ms = (time.perf_counter() - start_time) * 1000

    # Validate output equality
    pd.testing.assert_frame_equal(
        original_result.sort_values(by="customer_segment").reset_index(drop=True),
        refactored_result.sort_values(by="customer_segment").reset_index(drop=True),
        check_dtype=False
    )
    print("✔ Validation Passed: Nested subquery and CTE query return identical analytical results.\n")

    print("Refactored CTE Query Result:")
    print(refactored_result.to_string(index=False))
    print(f"\nNested Subquery Exec Time: {original_time_ms:.2f} ms")
    print(f"Refactored CTE Exec Time:  {refactored_time_ms:.2f} ms")
    print("=" * 80 + "\n")

    return {
        "original_time_ms": original_time_ms,
        "refactored_time_ms": refactored_time_ms,
        "result_df": refactored_result
    }

if __name__ == "__main__":
    run_task_3()
