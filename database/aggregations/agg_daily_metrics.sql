-- Pre-Aggregated Table: agg_daily_metrics
-- Grain: Daily (aggregation_date) grouped by metric_name
-- Purpose: Accelerate analytical dashboard rendering by pre-computing daily revenue and order metrics
-- Refresh Pattern: Scheduled batch ETL / ELT pipeline (e.g. daily cron / Airflow / dbt)
-- Updated: Monitored via the updated_at timestamp column for data freshness and SLA tracking
-- Used by: Streamlit Executive Dashboard, Real-time Sales Trend Monitors, Fast BI Visualizations
--
-- Columns:
--   aggregation_date: Calendar date of metric aggregation (YYYY-MM-DD)
--   metric_name: Standardized metric identifier (e.g., 'total_revenue', 'completed_orders')
--   metric_value: Numeric pre-computed aggregate value
--   row_count: Number of source transaction records summarized in this aggregate row
--   updated_at: Timestamp when this aggregate record was computed / refreshed

-- 1. Table DDL Definition
CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    row_count INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (aggregation_date, metric_name)
);

-- 2. Incremental / Batch Refresh Insertion Query
INSERT OR REPLACE INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
SELECT 
    DATE(o.order_date) AS aggregation_date,
    'total_revenue' AS metric_name,
    SUM(o.order_amount) AS metric_value,
    COUNT(*) AS row_count,
    CURRENT_TIMESTAMP AS updated_at
FROM orders o
WHERE o.status = 'Completed'
GROUP BY DATE(o.order_date);
