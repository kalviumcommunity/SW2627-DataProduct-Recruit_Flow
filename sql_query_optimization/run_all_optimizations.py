"""
Master Runner Script for Analytical SQL Query Optimization.
Executes Tasks 1, 2, and 3, collects performance and memory metrics,
and renders the comprehensive Task 4 comparison summary table.
"""

import os
import sys
import pandas as pd
from database_setup import create_and_populate_database, get_engine
from task1_explicit_columns import run_task_1
from task2_early_filtering import run_task_2
from task3_cte_readability import run_task_3

def main():
    db_file = "analytics.db"
    
    # 1. Initialize analytical database if not already present
    if not os.path.exists(db_file):
        print(f"Database {db_file} not found. Generating sample data...")
        create_and_populate_database(db_file, num_transactions=30000, num_customers=1000, num_products=100)
    else:
        print(f"Using existing analytical database: {db_file}\n")

    # 2. Execute Task 1
    t1_metrics = run_task_1()

    # 3. Execute Task 2
    t2_metrics = run_task_2()

    # 4. Execute Task 3
    t3_metrics = run_task_3()

    # 5. Task 4: Print Comparison Summary Table
    print("=" * 80)
    print("TASK 4: COMPREHENSIVE QUERY OPTIMIZATION COMPARISON")
    print("=" * 80)

    comparison = pd.DataFrame({
        'Metric': [
            'Query 1: Columns Selected', 
            'Query 1: Memory Footprint',
            'Query 2: Intermediate Join Rows', 
            'Query 2: Early Predicate Pushdown',
            'Query 3: Subquery Nesting Depth', 
            'Query 3: Code Readability & Modularity',
            'Query 3: Independent Unit Testability'
        ],
        'Original (Inefficient)': [
            f"{t1_metrics['original_cols']} cols (SELECT *)", 
            f"{t1_metrics['original_mem_kb']:.1f} KB",
            f"{t2_metrics['transactions_count']:,} rows (Full Table)", 
            'No (Joins then Filters)',
            '3 Levels (Nested Subqueries)', 
            'Hard to follow (Inside-out flow)',
            'No (Cannot test stages in isolation)'
        ],
        'Optimized (Production-Grade)': [
            f"{t1_metrics['optimized_cols']} explicit cols ({t1_metrics['col_reduction_pct']:.1f}% reduction)", 
            f"{t1_metrics['optimized_mem_kb']:.1f} KB ({t1_metrics['mem_reduction_pct']:.1f}% reduction)",
            f"{t2_metrics['filtered_transactions']:,} rows ({t2_metrics['reduction_factor']:.2f}x reduction)", 
            'Yes (Filtered CTE / Subquery)',
            '1 Level (Declarative CTEs)', 
            'Clear linear steps (Top-to-bottom)',
            'Yes (Each CTE independently testable)'
        ]
    })

    print(comparison.to_string(index=False))
    print("=" * 80)
    print("All optimization tasks and benchmarks executed successfully!")

if __name__ == "__main__":
    main()
