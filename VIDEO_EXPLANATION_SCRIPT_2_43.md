# 🎬 Video Explanation Script: SQL Views & Aggregation Layer Design (3–5 Minutes)

> **Speaker Instructions:** Ensure your webcam is turned ON with your face clearly visible. Share your screen displaying the codebase in VS Code / IDE. Maintain a clear, enthusiastic, and confident tone. Runtime: ~3 to 4.5 minutes.

---

## ⏱️ Video Structure & Visual Timing

| Timestamp | Segment | Visual Cue On Screen |
| :--- | :--- | :--- |
| **0:00 – 0:35** | Introduction & The Problem of Metric Drift | Open [`data_layer_conventions.md`](file:///Users/fibafathima/Documents/Recruit%20flow/data_layer_conventions.md) |
| **0:35 – 1:20** | Task 1: SQL Views (`vw_active_customers` & `vw_product_performance`) | Show [`database/views/vw_active_customers.sql`](file:///Users/fibafathima/Documents/Recruit%20flow/database/views/vw_active_customers.sql) |
| **1:20 – 2:05** | Task 2: Pre-Aggregated Table (`agg_daily_metrics`) | Show [`database/aggregations/agg_daily_metrics.sql`](file:///Users/fibafathima/Documents/Recruit%20flow/database/aggregations/agg_daily_metrics.sql) |
| **2:05 – 2:50** | Task 3 & 4: Python Dashboard Simulation & Naming Standards | Run [`assignment-33-python.py`](file:///Users/fibafathima/Documents/Recruit%20flow/assignment-33-python.py) in Terminal |
| **2:50 – 3:45** | Follow-Up Technical Answers (Propagation, Real-Time Lambda, QA Testing) | Show [`FOLLOW_UP_ANSWERS_2_43.md`](file:///Users/fibafathima/Documents/Recruit%20flow/FOLLOW_UP_ANSWERS_2_43.md) |
| **3:45 – 4:15** | Summary & Conclusion | Show final summary output in terminal |

---

## 🎙️ Spoken Script (Word-for-Word Guide)

### 1. Introduction (0:00 – 0:35)
> *"Hello everyone! Today, I am presenting our work on **SQL Views & Aggregation Layer Design**.*
>
> *In scaling analytics teams, a common failure mode is 'metric drift'—where Sales, Customer Success, and Operations calculate key metrics like revenue or active users independently in their own dashboard queries. This leads to conflicting numbers, meeting disputes, and slow dashboard queries.*
>
> *To solve this, we designed and implemented a clean, decoupled data layer using centralized SQL views as the single source of truth and pre-aggregated tables for high-speed dashboard performance."*

---

### 2. Task 1: Creating Centralized SQL Views (0:35 – 1:20)
*(Show `database/views/vw_active_customers.sql` and `vw_product_performance.sql`)*

> *"In **Task 1**, we defined two core SQL views following our strict `vw_` naming convention:*
>
> * **First, `vw_active_customers`:** *This view joins customers and orders to calculate a rolling 30-day activity window—tracking order frequency, 30-day revenue, last order timestamp, and days since last purchase, while filtering out soft-deleted accounts.*
> * **Second, `vw_product_performance`:** *Our custom metric view joins product catalogs with order data to evaluate sales velocity, cumulative revenue, and gross profit margins per product.*
>
> *Because views store query logic rather than data, these definitions ensure that any dashboard querying them receives 100% fresh, consistent metrics every single time."*

---

### 3. Task 2: High-Performance Pre-Aggregated Tables (1:20 – 2:05)
*(Show `database/aggregations/agg_daily_metrics.sql`)*

> *"While dynamic views are great for flexibility, scanning raw transactional logs on every dashboard refresh causes bottlenecks on large datasets.*
>
> *In **Task 2**, we implemented a pre-aggregated summary table named `agg_daily_metrics` at the daily grain.*
> * *It encapsulates pre-computed daily revenues, completed order counts, and crucially, an **`updated_at`** timestamp.*
> * *The `updated_at` column enables our dashboards and data health monitors to verify data freshness and alert users if aggregations become stale.*
> * *Querying this pre-aggregated table executes in **less than 0.3 milliseconds**—making executive dashboard rendering virtually instantaneous."*

---

### 4. Task 3 & 4: Dashboard Simulation & Naming Standards (2:05 – 2:50)
*(Run `python3 assignment-33-python.py` in the terminal)*

> *"In **Task 3**, we simulated how a production Streamlit dashboard consumes this clean data layer via Python and SQLAlchemy.*
> * *Our script queries top active customers, product margin leaders, and daily aggregates without touching raw tables directly.*
>
> *In **Task 4**, we formalized our architectural standards in `data_layer_conventions.md`:*
> * *All logical views use the **`vw_`** prefix formatted as `vw_[entity]_[metric]`.*
> * *All physical rollups use the **`agg_`** prefix formatted as `agg_[grain]_[subject]` with mandatory `updated_at` and `row_count` auditing columns.*
> * *This makes the data warehouse intuitive and prevents ad-hoc query fragmentation."*

---

### 5. Follow-Up Technical Q&A (2:50 – 3:45)
*(Show `FOLLOW_UP_ANSWERS_2_43.md`)*

> *"Now, let's address the key follow-up questions:*
>
> * **1. Automatic View Propagation:** *When a view definition is updated, all dashboards automatically execute the new query on their next run because views store query logic dynamically, not persisted data.*
> * **2. Real-Time Metrics & Stale Batches:** *For hourly aggregation cycles, we employ the **Hybrid Lambda View Pattern**, creating a view that performs a `UNION ALL` between historical data from `agg_daily_metrics` and a lightweight scan of intraday real-time transactions.*
> * **3. QA & Pre-Release Testing:** *We validate data layers using source-to-target mathematical parity checks ($\sum \text{source} == \sum \text{target}$), grain uniqueness assertions, and automated CI/CD regression tests in GitHub Actions."*

---

### 6. Conclusion (3:45 – 4:15)
> *"By building a structured SQL view and aggregation layer, we eliminate metric drift, guarantee a single source of truth, and ensure blazing fast sub-second dashboards.*
>
> *All code, view files, and documentation have been committed to our `frontend` branch. Thank you!"*
