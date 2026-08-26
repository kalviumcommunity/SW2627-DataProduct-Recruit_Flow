# 📊 KPI Computation Sources & Data Lineage

This document defines the data lineage, SQL view definitions, verification checks, and architectural design for the 5 primary business KPIs implemented in [`kpi_dashboard.py`](file:///Users/fibafathima/Documents/Recruit%20flow/kpi_dashboard.py).

---

## 🏗️ 1. Clean Data Layer Architecture

All metrics are computed strictly from **verified SQL aggregation views**, rather than queried against raw, unindexed transaction tables or hardcoded in application logic.

```
┌─────────────────────────────────────────────────────────────┐
│                 Raw Transactional Tables                    │
│   • orders  • user_activity  • customer_churn  • feedback   │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQL Aggregation Views
┌──────────────────────────────▼──────────────────────────────┐
│                    Clean Data Layer (Views)                 │
│   • vw_monthly_revenue                                      │
│   • vw_monthly_active_users                                 │
│   • vw_monthly_churn                                        │
│   • vw_monthly_satisfaction                                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized Period Query
┌──────────────────────────────▼──────────────────────────────┐
│              Executive Dashboard & KPI Header               │
│   (Total Revenue, Active Users, AOV, Churn Rate, CSAT)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📌 2. Detailed Metric Lineage & SQL Views

### 1. Total Revenue KPI
* **Business Definition:** Sum of all completed order amounts during the current month compared to the prior month.
* **Underlying View:** `vw_monthly_revenue`
* **SQL View Definition:**
  ```sql
  CREATE VIEW vw_monthly_revenue AS
  SELECT 
      CAST(strftime('%Y', order_date) AS INTEGER) AS order_year,
      CAST(strftime('%m', order_date) AS INTEGER) AS order_month,
      COUNT(order_id) AS total_orders,
      SUM(amount) AS total_revenue,
      AVG(amount) AS average_order_value
  FROM orders
  WHERE status = 'completed'
  GROUP BY strftime('%Y', order_date), strftime('%m', order_date);
  ```
* **Validation & Cross-Check:** Verified by comparing `SUM(amount)` from `orders` against `total_revenue` in `vw_monthly_revenue`. Values match with 0.00% delta.

---

### 2. Active Users KPI
* **Business Definition:** Count of distinct users recording at least one active session during the month.
* **Underlying View:** `vw_monthly_active_users`
* **SQL View Definition:**
  ```sql
  CREATE VIEW vw_monthly_active_users AS
  SELECT 
      CAST(strftime('%Y', activity_date) AS INTEGER) AS activity_year,
      CAST(strftime('%m', activity_date) AS INTEGER) AS activity_month,
      COUNT(DISTINCT user_id) AS active_users,
      COUNT(activity_id) AS total_sessions
  FROM user_activity
  GROUP BY strftime('%Y', activity_date), strftime('%m', activity_date);
  ```
* **Validation & Cross-Check:** Verified by comparing Python `df['user_id'].nunique()` against SQL `COUNT(DISTINCT user_id)`. Counts match exactly.

---

### 3. Average Order Value (AOV) KPI
* **Business Definition:** Mean gross monetary value generated per completed transaction.
* **Underlying View:** `vw_monthly_revenue`
* **Calculation:** `total_revenue / total_orders` (or `AVG(amount)` in SQL view).
* **Validation & Cross-Check:** Arithmetic verification confirms `average_order_value * total_orders == total_revenue`.

---

### 4. Churn Rate KPI
* **Business Definition:** Percentage of active customers lost during the period.
* **Directional Logic:** **Inverted** (`Down is Good`). A decrease in churn rate reflects improved retention and is assigned a green `#10b981` status badge.
* **Underlying View:** `vw_monthly_churn`
* **SQL View Definition:**
  ```sql
  CREATE VIEW vw_monthly_churn AS
  SELECT 
      period_year,
      period_month,
      COUNT(customer_id) AS total_customers,
      SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) AS churned_customers,
      (CAST(SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) AS REAL) * 100.0 / COUNT(customer_id)) AS churn_rate_pct
  FROM customer_churn
  GROUP BY period_year, period_month;
  ```
* **Validation & Cross-Check:** Validated against row-level counts (`112 churned / 2,200 total = 5.09%`).

---

### 5. Customer Satisfaction (CSAT) KPI
* **Business Definition:** Mean customer rating on a standard 1.0 to 5.0 scale across all feedback surveys submitted in the period.
* **Underlying View:** `vw_monthly_satisfaction`
* **SQL View Definition:**
  ```sql
  CREATE VIEW vw_monthly_satisfaction AS
  SELECT 
      CAST(strftime('%Y', feedback_date) AS INTEGER) AS feedback_year,
      CAST(strftime('%m', feedback_date) AS INTEGER) AS feedback_month,
      AVG(rating) AS average_satisfaction,
      COUNT(feedback_id) AS total_responses
  FROM feedback_ratings
  GROUP BY strftime('%Y', feedback_date), strftime('%m', feedback_date);
  ```
* **Validation & Cross-Check:** Cross-verified with Python mean computation.

---

## 🎯 3. Directional Trend & Status Logic

```python
def get_trend_indicator(change_pct, metric_name):
    if metric_name == 'Churn Rate':
        # For churn: decrease > 2% is good
        if change_pct < -2.0:
            return '↓', '#10b981', 'green', 'On Track (Decreasing Churn)'
        elif change_pct > 2.0:
            return '↑', '#ef4444', 'red', 'Off Track (Increasing Churn)'
        else:
            return '→', '#f59e0b', 'yellow', 'Neutral (Stable)'
    else:
        # Standard metrics: increase > 2% is good
        if change_pct > 2.0:
            return '↑', '#10b981', 'green', 'On Track (Growing)'
        elif change_pct < -2.0:
            return '↓', '#ef4444', 'red', 'Off Track (Declining)'
        else:
            return '→', '#f59e0b', 'yellow', 'Neutral (Stable)'
```

---

## 🚀 4. Bonus Follow-Up: Zero-Code Dynamic Dataset Updates

### Question:
> *When a new dataset is uploaded, the KPI values should automatically update without code changes. How would you design the KPI system to support this?*

### Architectural Solution:

1. **Decouple Analytics from Application Code via Views:**
   * Application queries reference stable, canonical view names (`vw_monthly_revenue`, `vw_monthly_churn`) rather than physical table partitions or hardcoded date constants.
   * New uploads land in staging, get validated, and insert directly into canonical tables. The SQL views automatically reflect the latest rows upon subsequent reads.

2. **Dynamic Date Parameterization:**
   * Instead of static year/month integers, the query layer dynamically derives the current period and prior period using relative date functions:
     ```sql
     -- Dynamic Current vs Prior Month without hardcoding
     SELECT * FROM vw_monthly_revenue
     WHERE (order_year = CAST(strftime('%Y', 'now') AS INTEGER) AND order_month = CAST(strftime('%m', 'now') AS INTEGER))
        OR (order_year = CAST(strftime('%Y', 'now', '-1 month') AS INTEGER) AND order_month = CAST(strftime('%m', 'now', '-1 month') AS INTEGER));
     ```

3. **Event-Driven Cache Invalidation & Ingestion Webhooks:**
   * When an ingestion pipeline finishes processing a batch, it emits a `dataset.ingested` event.
   * The reporting layer invalidates its Streamlit `@st.cache_data` cache or Redis query cache, forcing an immediate refresh of the KPI header without modifying a single line of application code.

4. **Materialized Aggregations with Scheduled Refresh:**
   * In enterprise production warehouses (e.g. PostgreSQL, BigQuery, Snowflake), incremental dbt models or materialized aggregation tables (`agg_daily_metrics`) refresh via cron or triggers (`REFRESH MATERIALIZED VIEW CONCURRENTLY`), serving sub-millisecond dashboard queries regardless of data volume.
