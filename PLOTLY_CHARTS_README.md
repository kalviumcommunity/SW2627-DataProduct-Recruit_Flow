# 📈 Interactive Plotly Chart Design & Streamlit Integration

This directory contains the complete implementation, interactive HTML exports, and Streamlit application for **Interactive Plotly Chart Design**.

---

## 📁 Interactive Artifact Catalog

```
.
├── chart1_revenue_trend.html          # Task 1A: Daily Revenue Trend with Unified Hover & Rolling Average
├── chart2_product_performance.html    # Task 1B: Product Performance Horizontal Bar with Multi-Column Tooltip
├── chart3_metric_selector.html        # Task 2: Instant Metric Dropdown Switcher (Zero Page Reload)
├── chart4_interactive.html            # Task 3: Interactive Multi-Dimensional Scatter Explorer (Zoom/Pan/Lasso)
├── assignment-36-plotly.py            # Complete automated generation & benchmarking script
├── streamlit_plotly_app.py            # Task 4: Interactive Streamlit Dashboard embedding Plotly views
└── output_plotly/                     # Mirrored high-resolution interactive HTML charts directory
```

---

## 🎯 Task Breakdown & Technical Specifications

### Task 1: Create Two Plotly Charts with Hover Tooltips (1 Mark)

#### 1. Chart 1 — Daily Revenue Trend with Unified Hover
* **File:** [`chart1_revenue_trend.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart1_revenue_trend.html)
* **Design Strategy:**
  * Uses `hovermode='x unified'` so hovering over any point displays the formatted date, daily revenue, completed order count, and average order value simultaneously.
  * Formats currency amounts as `$%,.2f` and counts with thousands separators `%,d`.
  * Embeds an interactive temporal range slider (`rangeslider=dict(visible=True)`) below the chart.
  * Overlays a 7-day moving average dotted trendline in gold (`#f59e0b`).

#### 2. Chart 2 — Product Performance with Multi-Column Hover
* **File:** [`chart2_product_performance.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart2_product_performance.html)
* **Design Strategy:**
  * Horizontal ranked bar chart sorting products by revenue.
  * Rich `hovertemplate` displaying 5+ data fields:
    * Product Name (`%{y}`)
    * Category (`%{customdata[0]}`)
    * Total Revenue (`$%{x:,.2f}`)
    * Total Orders (`%{customdata[1]:,}`)
    * Average Order Value (`$%{customdata[2]:,.2f}`)
    * Gross Profit (`$%{customdata[3]:,.2f}`)
    * Gross Profit Margin Percentage (`%{customdata[4]:.1f}%`)

---

### Task 2: Create Dropdown Filter to Toggle Views (1 Mark)

* **File:** [`chart3_metric_selector.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart3_metric_selector.html)
* **Design Strategy:**
  * Implemented using Plotly's client-side `updatemenus` dropdown feature.
  * Pre-loads three traces (**Revenue**, **Gross Profit**, and **Order Count**) into the figure.
  * Toggles the trace visibility array (`[True, False, False]`, `[False, True, False]`, `[False, False, True]`) and updates the Y-axis title and number formatting dynamically.
  * **Zero Page Reload:** All metric switching happens entirely client-side in the browser without database roundtrips.

---

### Task 3: Enable Zoom, Pan, Box/Lasso Select, and Reset (1 Mark)

* **File:** [`chart4_interactive.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart4_interactive.html)
* **Design Strategy:**
  * Multi-dimensional scatter plot comparing **Order Amount ($)** vs. **Gross Profit ($)** across customer segments (Enterprise, Mid-Market, SMB, Startup), with bubble sizes encoding quantity.
  * Configured with `dragmode='zoom'`, `hovermode='closest'`, and Plotly modebar tools.
  * **Interactions Supported:**
    1. **Zoom:** Click and drag a bounding box over any coordinate region.
    2. **Pan:** Hold `Shift` + click and drag to pan across axes.
    3. **Reset:** Double-click anywhere on the canvas to restore full zoom extents.
    4. **Box / Lasso Selection:** Select and isolate specific enterprise outlier clusters.

---

### Task 4: Integrate Plotly into Streamlit (1 Mark)

* **File:** [`streamlit_plotly_app.py`](file:///Users/fibafathima/Documents/Recruit%20flow/streamlit_plotly_app.py)
* **Features:**
  * Embedded Plotly figures using `st.plotly_chart(fig, use_container_width=True)`.
  * **Dynamic Sidebar Filters:**
    * Date range picker (`st.sidebar.date_input`)
    * Minimum order amount slider (`st.sidebar.slider`)
    * Product category multi-select (`st.sidebar.multiselect`)
    * Customer segment filter (`st.sidebar.multiselect`)
  * **Dynamic KPI Summary Cards:** Total Revenue, Gross Profit, Total Orders, and Average Order Value.
  * **Tabbed Navigation:** Clean switching between Revenue Trends, Product Performance, Metric Switcher, and Multi-Dimensional Explorer.
  * **Data Export:** Filtered tabular preview with one-click CSV download.

---

## 🚀 Execution & Verification

1. **Generate All 4 Standalone HTML Charts:**
   ```bash
   python3 assignment-36-plotly.py
   ```

2. **Run Interactive Streamlit Analytics Dashboard:**
   ```bash
   streamlit run streamlit_plotly_app.py
   ```
