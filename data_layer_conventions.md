# 📐 Clean Data Layer Naming Conventions & Design Standards

---

## 1. SQL Views

* **Prefix:** `vw_`
* **Pattern:** `vw_[business_entity]_[metric_or_focus]`
* **Purpose:** Encapsulate business metric definitions into a single, centralized logical query layer that serves as the single source of truth across all BI tools, dashboards, and notebooks.

### Examples:
* `vw_active_customers`: Customer recency, 30-day order frequency, and short-term revenue contribution.
* `vw_product_performance`: Product velocity, gross margins, unit costs, and cumulative revenue.
* `vw_revenue_by_region`: Regional sales breakdown and country-level revenue metrics.
* `vw_churn_risk_cohorts`: Candidate or customer engagement scoring and inactivity indicators.

---

## 2. Pre-Aggregated Tables

* **Prefix:** `agg_`
* **Pattern:** `agg_[grain]_[subject]`
* **Purpose:** Pre-compute expensive multi-table joins, distinct counts, and large aggregations into physical tables to provide instant (< 5ms) dashboard response times.

### Examples:
* `agg_daily_metrics`: Daily aggregated business KPIs (e.g. daily revenue, order volumes).
* `agg_monthly_churn`: Monthly customer cohort retention and churn rates.
* `agg_hourly_traffic`: High-frequency hourly web and transactional throughput metrics.

---

## 3. Required Columns in Pre-Aggregated Tables

Every `agg_` table in the database must strictly adhere to the following schema conventions:

| Column Requirement | Naming Convention | Description & Rationale |
| :--- | :--- | :--- |
| **Grain Identifier** | `aggregation_date` / `hour_bucket` / `customer_id` | Explicitly defines the dimensional level of aggregation (e.g. daily, hourly, entity level). |
| **Data Freshness Timestamp** | `updated_at` / `created_at` | Tracks when the aggregation batch was computed to detect data staleness and monitor SLA freshness. |
| **Source Row Count** | `row_count` | Number of underlying transactional records summarized; critical for data auditing and integrity validation. |
| **Metric Dimensions** | `metric_name`, `metric_value` | Standardized key-value or columnar metric definitions avoiding ambiguous column names. |

---

## 4. Key Architectural Benefits

1. **Elimination of Metric Drift:** Business metrics (such as "Revenue" or "Active Customers") are defined in one centralized SQL view. When business logic evolves, updating the view automatically propagates to all consumers.
2. **Instant Dashboard Performance:** Dashboards query lightweight `agg_` tables or filtered views rather than scanning millions of raw transactional records.
3. **Self-Documenting Codebase:** Developers and data analysts immediately understand whether an object is a raw relation, a dynamic metric view (`vw_`), or a pre-computed rollup table (`agg_`).
4. **Decoupled Architecture:** Downstream BI dashboards and frontend applications never query raw transactional tables directly, shielding them from underlying schema migrations.

---

## 5. Applied Conventions in this Repository

| Object Name | Object Type | Grain / Focus | Schema / File Location |
| :--- | :--- | :--- | :--- |
| **`vw_active_customers`** | Dynamic SQL View | Customer Entity (30-day window) | [`database/views/vw_active_customers.sql`](file:///Users/fibafathima/Documents/Recruit%20flow/database/views/vw_active_customers.sql) |
| **`vw_product_performance`** | Dynamic SQL View | Product Entity (Sales & Margin) | [`database/views/vw_product_performance.sql`](file:///Users/fibafathima/Documents/Recruit%20flow/database/views/vw_product_performance.sql) |
| **`agg_daily_metrics`** | Pre-Aggregated Table | Daily Grain (`aggregation_date`) | [`database/aggregations/agg_daily_metrics.sql`](file:///Users/fibafathima/Documents/Recruit%20flow/database/aggregations/agg_daily_metrics.sql) |
