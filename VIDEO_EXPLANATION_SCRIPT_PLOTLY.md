# 🎬 Video Explanation Script: Interactive Plotly Chart Design (3–5 Minutes)

> **Speaker Instructions:** Ensure your webcam is turned ON with your face clearly visible. Share your screen displaying either `streamlit_plotly_app.py` in the browser or the interactive HTML files. Interact with the charts live (hover, zoom, switch dropdown). Runtime: ~3.5 to 4.5 minutes.

---

## ⏱️ Visual Timing & Topic Breakdown

| Timestamp | Visual Cue | Segment Topic |
| :--- | :--- | :--- |
| **0:00 – 0:35** | Show `streamlit_plotly_app.py` running in browser | Introduction & Why Interactive Plotly Visualizations Matter |
| **0:35 – 1:15** | Open Tab 1 (`chart1_revenue_trend.html`) | Task 1A: Daily Revenue Trend with Unified Hover & Range Slider |
| **1:15 – 1:55** | Open Tab 2 (`chart2_product_performance.html`) | Task 1B: Product Performance with Multi-Column Rich Hover |
| **1:55 – 2:35** | Open Tab 3 (`chart3_metric_selector.html`) | Task 2: Client-Side Dropdown Metric Switcher (Zero Reload) |
| **2:35 – 3:15** | Open Tab 4 (`chart4_interactive.html`) | Task 3: Native Plotly Controls (Zoom, Pan, Lasso, Double-Click Reset) |
| **3:15 – 4:00** | Interact with Streamlit Sidebar Filters | Task 4: Streamlit Dashboard Integration & Reactive Filtering |
| **4:00 – 4:30** | Show Summary Table | Conclusion & Production Takeaways |

---

## 🎙️ Spoken Script (Word-for-Word Guide)

### 1. Introduction (0:00 – 0:35)
> *"Hello everyone! Today, I am presenting our work on **Interactive Plotly Chart Design and Streamlit Integration**.*
>
> *Static charts are useful for print reports, but modern decision-makers need interactive data apps that allow them to explore multiple dimensions on demand, inspect specific outlier records through tooltips, and dynamically switch metrics without waiting for database re-queries.*
>
> *In this project, we built a suite of four rich Plotly visualizations and integrated them into a reactive Streamlit analytics dashboard."*

---

### 2. Task 1: Rich Hover Tooltips & Time-Series (0:35 – 1:15)
*(Hover over points in Chart 1 / Tab 1)*

> *"In **Task 1**, we designed two charts featuring custom `hovertemplate` configurations:*
>
> * **Chart 1: Daily Revenue Trend:** *Here we enabled `hovermode='x unified'` and added custom data attributes so that hovering over any point displays the formatted date, daily revenue, completed order count, and average order value simultaneously. We also added an interactive range slider below for flexible temporal exploration.*
> * **Chart 2: Product Performance:** *Our horizontal ranking bar chart displays 5 custom data dimensions on hover—product category, total revenue, order count, average order value, and gross profit margin percentage."*

---

### 3. Task 2: Dropdown Metric Switcher without Page Reload (1:15 – 1:55)
*(Click the dropdown menu in Chart 3 / Tab 3 and toggle between Revenue, Profit, and Orders)*

> *"In **Task 2**, we implemented a client-side metric switcher using Plotly's `updatemenus` feature.*
>
> *Notice that when I click the dropdown to switch from **Revenue** to **Gross Profit** or **Order Volume**, the visualization transitions instantly without a browser reload or database roundtrip.*
> * *We achieved this by pre-loading all three traces into the Plotly figure and toggling their visibility array (`[True, False, False]`) while dynamically updating the Y-axis title and formatting."*

---

### 4. Task 3: Native Zoom, Pan, Lasso, and Reset Controls (1:55 – 2:35)
*(Click and drag to zoom into a cluster in Chart 4 / Tab 4, shift-drag to pan, then double-click to reset)*

> *"In **Task 3**, we enabled native interactive controls on a multi-dimensional order profitability scatter plot:*
> * *Viewers can **click and drag** to zoom into high-density clusters.*
> * *Holding **Shift and dragging** allows smooth panning across coordinate planes.*
> * *Using the top modebar, we can activate **Lasso or Box Selection** to isolate high-value enterprise accounts.*
> * *And a simple **double-click** resets the view back to its full extent."*

---

### 5. Task 4: Streamlit Dashboard Integration (2:35 – 3:30)
*(Adjust the Min Order Amount slider and multiselect category filters in the sidebar)*

> *"In **Task 4**, we integrated all of these Plotly components into a production Streamlit application.*
> * *Using `st.plotly_chart(fig, use_container_width=True)`, the charts respond seamlessly to screen resize events.*
> * *Our sidebar provides reactive filtering by date range, product category, customer segment, and minimum order amount.*
> * *When a user adjusts a filter, all KPI summary cards, interactive tabs, and the underlying data table update reactively in real time, with an instant CSV export option."*

---

### 6. Summary & Conclusion (3:30 – 4:00)
> *"By combining Plotly's client-side interactivity with Streamlit's reactive UI framework, we provide business users with a fast, self-service data exploration tool that minimizes cognitive load and empowers data-driven decisions.*
>
> *All code, HTML exports, and documentation have been committed and pushed to the `frontend` branch. Thank you!"*
