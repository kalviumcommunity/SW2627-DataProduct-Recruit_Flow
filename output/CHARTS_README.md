# 📊 Business Visualisation Portfolio & Technical Documentation

This document provides complete documentation for the five business visualizations created in accordance with **2.45 Business Visualisation Principles**. Every chart has been crafted to match its specific data relationship, fully labeled, styled with an accessible cohesive color palette, and enriched with actionable business annotations.

---

## 🎨 Global Design System & Accessibility Palette

All charts strictly adhere to the unified, color-blind accessible palette:

```python
PALETTE = {
    'primary':       '#1f77b4',  # Steel Blue - Dominant series / Base category
    'secondary':     '#ff7f0e',  # Warm Amber - Secondary series / Highlight
    'success':       '#2ca02c',  # Forest Green - Benchmarks, targets, positive peaks
    'danger':        '#d62728',  # Crimson Red - Trendlines, dips, anomalies, outliers
    'purple':        '#9467bd',  # Deep Violet - Tertiary category
    'neutral':       '#7f7f7f',  # Slate Gray - Baseline thresholds & grids
    'annotation_bg': '#fff3cd'   # Light Amber - High-contrast annotation callout box
}
```

### ♿ Accessibility & Color-Blindness Compliance
* **Multi-Channel Visual Encoding:** Color is never used as the sole conveyor of information. Multi-series charts pair color with unique marker glyphs (circles `o`, squares `s`, triangles `^`) and distinct line patterns (solid, dashed, dotted).
* **Direct Value Labeling:** Data values and thresholds are directly labeled on bars, peaks, and outliers, ensuring clarity even in monochrome or grayscale printing.
* **High Contrast Ratios:** Text and callout boxes meet WCAG AA contrast ratios against light background canvas elements (`#fafbfc`).

---

## 📈 Chart Catalog & Insight Documentation

---

### 1. Chart 1: Revenue by Product Line (Comparison)
* **File:** [`output/chart1_revenue_by_product.png`](file:///Users/fibafathima/Documents/Recruit%20flow/output/chart1_revenue_by_product.png)
* **Chart Type:** Horizontal Bar Chart
* **Data Relationship:** Discrete categorical comparison across product lines.
* **Business Question:** *Which product line generated the highest revenue in Q4 2024, and did categories exceed the quarterly benchmark?*
* **Complete Labeling:**
  * **Title:** `Q4 Total Revenue by Product Line (Comparison)`
  * **X-Axis:** `Revenue ($ in Millions)` with formatted currency ticks (`$1.0M`, `$2.0M`, etc.)
  * **Y-Axis:** `Product Line`
  * **Data Labels:** Direct `$X.XXM` text placed at the end of each bar.
* **Key Insight:** **AI & ML Services** leads the enterprise portfolio with **$3.45M** in Q4 revenue, followed by Cloud Infrastructure ($2.85M).
* **Annotations & Reference Lines:**
  * **Target Line:** Green dashed reference line at **$2.5M Quarterly Target**.
  * **Annotation Box:** Callout arrow highlighting AI & ML Services as the top performer contributing **30.5% of total Q4 revenue**.

---

### 2. Chart 2: Monthly Revenue Trend (Time-Series)
* **File:** [`output/chart2_revenue_trend.png`](file:///Users/fibafathima/Documents/Recruit%20flow/output/chart2_revenue_trend.png)
* **Chart Type:** Multi-Series Line Chart with Markers
* **Data Relationship:** Continuous chronological time-series over 12 months.
* **Business Question:** *How has monthly revenue evolved across the top 3 product lines throughout 2024, and where do seasonal fluctuations occur?*
* **Complete Labeling:**
  * **Title:** `2024 Monthly Revenue Trend Across Top 3 Products (Time-Series)`
  * **X-Axis:** `Month (Fiscal Year 2024)` across all 12 calendar months.
  * **Y-Axis:** `Monthly Revenue ($ in Thousands)` formatted as `$150K`, `$300K`, `$450K`.
  * **Legend:** Upper-left legend identifying AI & ML Services (`o`), Cloud Infrastructure (`s`), and Developer Tools (`^`).
* **Key Insight:** Consistent annual expansion across all lines, punctuated by a predictable summer slowdown in August followed by a strong Q4 acceleration.
* **Annotations & Reference Lines:**
  * **Seasonality Dip:** Callout arrow in August marking the enterprise budget pause ($235K dip).
  * **Year-End Peak:** Green callout box marking the December all-time record ($420K).
  * **Threshold:** Dotted reference line at the $300K Tier 1 benchmark.

---

### 3. Chart 3: Order Value Distribution (Distribution)
* **File:** [`output/chart3_order_value_distribution.png`](file:///Users/fibafathima/Documents/Recruit%20flow/output/chart3_order_value_distribution.png)
* **Chart Type:** Binned Histogram with Kernel Density Estimation (KDE) Curve
* **Data Relationship:** Probability density and distribution spread of continuous order values.
* **Business Question:** *What is the typical customer purchase amount, and does customer purchasing behavior follow single or multi-tier clusters?*
* **Complete Labeling:**
  * **Title:** `Distribution of Transaction Order Values (Bimodal Population)`
  * **X-Axis:** `Order Value ($ USD)` formatted with dollar currency prefixes.
  * **Y-Axis:** `Transaction Frequency (Count)`
  * **Legend:** Upper-right legend detailing Mean and Median statistical reference lines.
* **Key Insight:** Reveals a distinct **bimodal distribution** proving that calculating a single overall average ($305) masks two distinct buyer personas.
* **Annotations & Reference Lines:**
  * **Cluster 1 Annotation:** Marks the Self-Serve / SMB tier peaking at **~$120**.
  * **Cluster 2 Annotation:** Marks the Enterprise tier peaking at **~$650**.
  * **Statistical Lines:** Red dashed line for Mean ($305) and green dotted line for Median ($180).

---

### 4. Chart 4: Quarterly Revenue Composition (Part-to-Whole)
* **File:** [`output/chart4_revenue_composition.png`](file:///Users/fibafathima/Documents/Recruit%20flow/output/chart4_revenue_composition.png)
* **Chart Type:** Stacked Bar Chart
* **Data Relationship:** Composition and total contribution across discrete quarters.
* **Business Question:** *How is our overall revenue mix shifting between legacy infrastructure and high-growth AI services over the four fiscal quarters?*
* **Complete Labeling:**
  * **Title:** `Quarterly Revenue Composition by Product Line (2024 Fiscal Year)`
  * **X-Axis:** `Fiscal Quarter` (`Q1 2024` through `Q4 2024`)
  * **Y-Axis:** `Total Revenue ($ in Millions)` formatted as `$2.0M`, `$4.0M`, etc.
  * **Total Value Labels:** Bold totals on top of each stacked bar ($7.10M in Q1 to $10.05M in Q4).
  * **Legend:** Product line color breakdown.
* **Key Insight:** Overall company revenue grew by **41.5%** over the year, driven disproportionately by AI & ML Services expanding from $1.8M in Q1 to $3.45M in Q4 (+91.6% YoY).
* **Annotations & Reference Lines:**
  * **Portfolio Shift Callout:** Red arrow pointing to the expanding AI/ML segment in Q4.

---

### 5. Chart 5: Marketing Spend vs. Generated Revenue (Correlation)
* **File:** [`output/chart5_marketing_vs_revenue.png`](file:///Users/fibafathima/Documents/Recruit%20flow/output/chart5_marketing_vs_revenue.png)
* **Chart Type:** Scatter Plot with Fitted Ordinary Least Squares (OLS) Regression Trendline
* **Data Relationship:** Bivariate correlation between marketing expenditure and revenue return.
* **Business Question:** *Does higher regional marketing investment reliably drive top-line revenue, and are there campaign anomalies?*
* **Complete Labeling:**
  * **Title:** `Correlation Analysis: Marketing Campaign Spend vs. Generated Revenue`
  * **X-Axis:** `Marketing Campaign Spend ($ in Thousands)` formatted as `$20K`, `$60K`, `$100K`.
  * **Y-Axis:** `Revenue Generated ($ in Millions)` formatted as `$1.0M`, `$3.0M`, `$5.0M`.
  * **Legend:** Identifies campaign scatter points and the linear regression trendline ($r = 0.84$).
* **Key Insight:** Demonstrates a **strong positive linear relationship ($r = 0.84$)**, validating that campaigns above $90K spend consistently generate over $4.0M in revenue.
* **Annotations & Reference Lines:**
  * **Outlier Callout:** Arrow identifying a campaign anomaly with high spend ($112K) but depressed revenue ($1.25M) caused by a localized channel launch delay.
  * **High ROI Cluster Callout:** Green badge marking the top-performing campaign cluster.

---

## 🛠️ Reproduction & Automated Generation

To re-generate all five visualizations at 300 DPI:

```bash
python3 assignment-35-visualizations.py
```
