# 📈 Interactive Plotly Chart Design & Streamlit Integration

This directory contains the complete implementation, interactive HTML exports, and Streamlit application for **Interactive Plotly Chart Design**.

---

## 📁 Interactive Artifact Catalog

```
.
├── chart1_revenue_trend.html          # Task 1: Daily Revenue Trend with Unified Hover
├── chart2_product_performance.html    # Task 1: Product Performance with Multi-Column Rich Hover
├── chart3_metric_selector.html        # Task 2: Instant Metric Dropdown Switcher (No Reload)
├── chart4_interactive.html            # Task 3: Interactive Multi-Dimensional Scatter Explorer
├── assignment-36-plotly.py            # Complete automated generation & benchmarking script
├── streamlit_plotly_app.py            # Task 4: Interactive Streamlit Dashboard with Reactive Filters
├── output_plotly/                     # Mirrored high-resolution interactive HTML exports
└── VIDEO_EXPLANATION_SCRIPT_PLOTLY.md # Word-for-word 3-5 minute video presentation script
```

---

## 📊 Detailed Chart Specifications

### 1. Chart 1: Daily Revenue Trend with Unified Hover
* **File:** [`chart1_revenue_trend.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart1_revenue_trend.html)
* **Interaction Type:** Time-Series Line + Scatter with `hovermode='x unified'`.
* **Hover Data Elements:**
  * ISO Date (`%{x|%Y-%m-%d}`)
  * Daily Revenue (`$%{y:,.2f}`)
  * Completed Order Count (`%{customdata[0]:,}`)
  * Average Order Value (`$%{customdata[1]:,.2f}`)
  * 7-Day Rolling Moving Average Trendline.
* **Interactive Feature:** Includes an interactive **Range Slider** below the X-axis for smooth temporal zooming.

---

### 2. Chart 2: Product Performance with Multi-Column Rich Hover
* **File:** [`chart2_product_performance.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart2_product_performance.html)
* **Interaction Type:** Horizontal Ranked Bar Chart with Color Scale gradient.
* **Hover Data Elements:**
  * Product Name (`%{y}`) & Category (`%{customdata[0]}`)
  * Total Revenue (`$%{x:,.2f}`)
  * Total Completed Orders (`%{customdata[1]:,}`)
  * Average Order Value (`$%{customdata[2]:,.2f}`)
  * Total Gross Profit (`$%{customdata[4]:,.2f}`)
  * Gross Margin Percentage (`%{customdata[3]:.1f}%`)

---

### 3. Chart 3: Metric Selector Dropdown Filter (Zero Reload)
* **File:** [`chart3_metric_selector.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart3_metric_selector.html)
* **Interaction Type:** Dropdown Updatemenus modifying trace visibility client-side without re-querying the database.
* **Dropdown Options:**
  1. `📊 Total Revenue ($)`: Activates Revenue trace (`visible: [True, False, False]`).
  2. `💰 Gross Profit ($)`: Activates Profit trace (`visible: [False, True, False]`).
  3. `📦 Order Volume (Count)`: Activates Order Count trace (`visible: [False, False, True]`).
* **Dynamic Layout:** Dropdown dynamically re-labels the Y-axis and title to match the active metric.

---

### 4. Chart 4: Multi-Dimensional Order Explorer (Zoom / Pan / Lasso)
* **File:** [`chart4_interactive.html`](file:///Users/fibafathima/Documents/Recruit%20flow/chart4_interactive.html)
* **Interaction Type:** Multi-Dimensional Scatter Plot with 5 data dimensions (X: Order Amount, Y: Order Profit, Color: Category, Size: Order Amount, Hover: Customer Segment, Order ID, Date).
* **Native Interaction Modes Supported:**
  * **Zoom:** Click and drag on any canvas area to zoom in.
  * **Pan:** Shift + drag to pan horizontally and vertically.
  * **Reset:** Double-click anywhere to reset to full extent.
  * **Box / Lasso Selection:** Select arbitrary subsets of data points with persistent highlight.

---

## 💻 Task 4: Streamlit Reactive Dashboard Integration

The dashboard in [`streamlit_plotly_app.py`](file:///Users/fibafathima/Documents/Recruit%20flow/streamlit_plotly_app.py) embeds all four Plotly charts with bidirectional reactive filtering:

### Features:
1. **Sidebar Filter Widgets:**
   * Dynamic Date Range Picker (`st.sidebar.date_input`)
   * Product Category Multiselect (`st.sidebar.multiselect`)
   * Customer Segment Multiselect (`st.sidebar.multiselect`)
   * Min Order Amount Value Slider (`st.sidebar.slider`)
2. **Executive KPI Cards:** Real-time updates for Total Revenue, Gross Profit, Total Orders, and Average Order Value.
3. **Tabbed Navigation:** Seamlessly toggles between Daily Trends, Product Rankings, Dynamic Metric Switcher, and the Order Explorer.
4. **Data Export:** Instant CSV download of the filtered dataset.

### Launch Streamlit Dashboard:
```bash
streamlit run streamlit_plotly_app.py
```

---

## 🛠️ Automated Standalone Generator

To re-generate all standalone interactive HTML charts:

```bash
python3 assignment-36-plotly.py
```
