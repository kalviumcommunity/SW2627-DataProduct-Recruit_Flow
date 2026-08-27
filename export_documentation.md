# 📦 Analysis Report & Automated Export Guide

Welcome to the **Customer Churn & Support Velocity Automated Reporting Guide**. This document explains the structure, use cases, and update schedules for all generated analysis export files.

---

## 📁 What's Included in Each Export

Whenever an analysis export is triggered—either on-demand through our Streamlit dashboard or via the automated daily scheduler—a timestamped folder (`output/YYYY-MM-DD_HHMM_analysis/`) is created with four synchronized artifacts:

### 1. `cleaned_data.csv`
* **Purpose:** Cleaned, structured tabular records for deep-dive analysis, ad-hoc querying, and pivot table modeling in Microsoft Excel, Google Sheets, or SQL databases.
* **Scope:** 50,000 customer accounts across the 24-month longitudinal study.
* **Schema Columns:**
  * `customer_id`: Unique account identifier
  * `customer_segment`: Tier classification (`Enterprise`, `Mid-Market`, `SMB`, `Startup`)
  * `annual_revenue`: Annual Contract Value (ACV / ARR in USD)
  * `support_response_hours`: First response latency in hours
  * `support_tickets_count`: Total logged support tickets
  * `renewal_status`: Renewal state (`Renewed` vs. `Churned`)
* **Use Case:** Financial modeling, custom segmentation, and analyst exploration.
* **Refresh Schedule:** Updated daily at 5:00 PM EST and on-demand.

---

### 2. `summary_report.pdf`
* **Purpose:** Executive summary and business case formatted for leadership meetings, board decks, and email distribution.
* **Content:**
  * Problem context ($2.0M annual churn loss, 7.0% vs. 4.0% industry benchmark)
  * Key empirical findings (2-hour retention threshold, 4x risk escalation)
  * Operational bottleneck analysis (6.2-hour team average)
  * Three prioritized, high-ROI recommendations ($400K gross ARR recovered, +$200K net Year-1 gain)
  * Actionable decision roadmap and milestone schedule
* **Length:** 2 pages, publication-ready vector styling.
* **Use Case:** Executive briefings, budget approval presentations, and cross-functional alignment.

---

### 3. `interactive_report.html`
* **Purpose:** Complete standalone interactive dashboard report requiring zero Python installations.
* **Content:**
  * Executive markdown narrative and summary tables.
  * Embedded **interactive Plotly figures** with unified tooltips, zoom, pan, and hover capabilities.
* **Size:** Single self-contained HTML file (loads Plotly via CDN).
* **Use Case:** Share via email or internal Slack; opens directly in Chrome, Safari, Firefox, or Edge on any desktop or mobile device.
* **Interactions Supported:** Hover over data points to inspect exact figures, drag to zoom into clusters, and toggle trace visibility in legends.

---

### 4. `README.md` (Metadata & Data Lineage)
* **Purpose:** Traceable audit trail capturing timestamped metadata, record counts, schema definitions, and cohort temporal boundaries for enterprise governance.

---

## 🛠️ How to Use These Files

1. **For Excel / Spreadsheet Modeling:** Open `cleaned_data.csv` in Excel or Sheets to build custom pivot tables, segment filters, and correlation models.
2. **For Executive Presentations:** Print or email `summary_report.pdf` directly to stakeholders and C-suite leadership.
3. **For Visual Data Exploration:** Double-click `interactive_report.html` in any browser to explore charts with rich tooltips, zoom into specific tiers, and inspect underlying data distributions.
4. **For Frictionless Sharing:** Attach `interactive_report.html` to emails—recipients need no special software or Python environment to interact with the visualizations.

---

## ⏰ When Are These Files Updated?

* **Daily Automated Refresh (5:00 PM EST):** The automated batch runner ([`export_functions.py`](file:///Users/fibafathima/Documents/Recruit%20flow/export_functions.py)) generates a fresh timestamped export package every evening.
* **On-Demand Real-Time Export:** Business users can click the **`📥 Export Analysis Package`** button in the [`streamlit_export_integration.py`](file:///Users/fibafathima/Documents/Recruit%20flow/streamlit_export_integration.py) dashboard to immediately generate and download updated CSV, PDF, or HTML artifacts.

---

## ❓ Frequently Asked Questions & References

* **Where can I see the statistical model and equations?**  
  See [`technical_analysis.md`](file:///Users/fibafathima/Documents/Recruit%20flow/technical_analysis.md) for full logistic regression coefficients, $M/M/c$ Erlang-C queue formulations, $p$-values, and AUC metrics.
* **Where can I find the 1-page executive brief?**  
  See [`executive_summary.md`](file:///Users/fibafathima/Documents/Recruit%20flow/executive_summary.md).
* **Where can I review stakeholder-tailored versions?**  
  See [`audience_versions_A_B_C.md`](file:///Users/fibafathima/Documents/Recruit%20flow/audience_versions_A_B_C.md).
