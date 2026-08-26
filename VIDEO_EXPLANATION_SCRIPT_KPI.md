# 🎬 Video Explanation Script: Executive KPI Dashboard Design (3–5 Minutes)

> **Speaker Instructions:** Turn on your webcam with your face clearly visible. Share your screen displaying either `kpi_dashboard.py` execution output in terminal or the Streamlit web dashboard. Runtime: ~3.5 to 4.5 minutes.

---

## ⏱️ Visual Timing & Topic Breakdown

| Timestamp | Visual Cue | Segment Topic |
| :--- | :--- | :--- |
| **0:00 – 0:40** | Show Streamlit KPI Header / Terminal Output | Introduction & Purpose of Executive KPI Cards |
| **0:40 – 1:30** | Highlight 5 KPI Metric Cards | Task 1 & 3: Computing 5 Core KPIs & Period-over-Period Changes |
| **1:30 – 2:20** | Point to Churn Card vs Revenue Card | Task 2: Directional Trend Indicators & Inverted Churn Logic |
| **2:20 – 3:10** | Show `kpi_sources.md` and SQL Views | Task 5: Clean SQL Data Layer & Verification Cross-Checks |
| **3:10 – 4:00** | Point to Architecture Diagram in `kpi_sources.md` | Bonus: Dynamic Dataset Updates without Code Changes |
| **4:00 – 4:30** | Show Detailed Analytical Charts | Conclusion & Summary |

---

## 🎙️ Spoken Script (Word-for-Word Guide)

### 1. Introduction (0:00 – 0:40)
> *"Hello everyone! Today, I am presenting our implementation of the **Executive KPI Dashboard Header and Data Lineage Architecture**.*
>
> *Business executives and decision-makers need to assess organizational health at a single glance. Rather than sifting through thousands of raw records, a dashboard header should summarize the top 5 operational metrics with clear values, percentage changes, directional trend arrows, and intuitive status indicators."*

---

### 2. Computing the 5 Core KPIs (0:40 – 1:30)
*(Point to the 5 KPI cards)*

> *"In **Task 1 and Task 3**, we compute five essential KPIs comparing the current month-to-date against the prior month:*
> 1. **Total Revenue:** *Measures overall gross sales volume.*
> 2. **Active Users:** *Tracks unique user engagement.*
> 3. **Average Order Value (AOV):** *Measures average spending per transaction.*
> 4. **Churn Rate:** *Quantifies customer attrition.*
> 5. **Customer Satisfaction (CSAT):** *Averages customer feedback ratings on a 5-star scale.*
>
> *All values are dynamically computed from our SQL data layer and formatted with clear delta percentages, such as `+18.9%` or `-12.2%`."*

---

### 3. Directional Trend Logic & Inverted Churn (1:30 – 2:20)
*(Hover over the Churn Rate card showing the green badge with downward arrow)*

> *"In **Task 2**, we implemented directional trend indicators:*
> * *For standard business metrics like Revenue, Users, AOV, and Satisfaction, **an increase is positive** (Green arrow up `↑`), and **a decrease is negative** (Red arrow down `↓`).*
> * *Crucially, for **Churn Rate**, the logic is **inverted**: a decrease in churn rate means customer retention is improving! Therefore, our engine assigns a green badge and downward arrow (`↓ -12.2%`) to celebrate reduced churn.*
> * *Changes within $\pm 2\%$ are flagged as neutral yellow (`→`)."*

---

### 4. Clean SQL Data Layer & Verification (2:20 – 3:10)
*(Open `kpi_sources.md`)*

> *"In **Task 5**, we ensured that no KPI values are hardcoded in application logic.*
> * *Every metric is powered by a dedicated SQL aggregation view: `vw_monthly_revenue`, `vw_monthly_active_users`, `vw_monthly_churn`, and `vw_monthly_satisfaction`.*
> * *We cross-verified the SQL view aggregations against Python arithmetic calculations, confirming identical results with 100% data integrity."*

---

### 5. Bonus: Zero-Code Dynamic Updates (3:10 – 4:00)
> *"For our follow-up question on supporting new dataset uploads without code changes:*
> * *We designed the KPI query layer to reference canonical view names and dynamic date arithmetic (`strftime('%Y', 'now')`) rather than hardcoded month integers.*
> * *When a new dataset is uploaded, it seamlessly flows into the underlying tables, and the SQL views immediately reflect updated metrics upon the next query.*
> * *In production, event-driven webhooks and materialized aggregation refreshes ensure sub-millisecond dashboard speeds without requiring any code redeployments."*

---

### 6. Conclusion (4:00 – 4:30)
> *"To summarize, we have built a modular, validated, and state-of-the-art KPI header backed by a robust SQL view architecture.*
>
> *All files including `kpi_dashboard.py`, `kpi_sources.md`, and this presentation script are committed and pushed to the repository. Thank you!"*
