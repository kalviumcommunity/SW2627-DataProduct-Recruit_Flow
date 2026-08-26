# 🎬 Video Explanation Script: Business Visualisation Principles (3–5 Minutes)

> **Speaker Instructions:** Ensure your camera is ON with your face clearly visible. Share your screen displaying the generated chart PNGs in VS Code or an image previewer. Speak clearly and walk through each chart methodically. Runtime: ~3.5 to 4.5 minutes.

---

## ⏱️ Visual Timing & Topic Breakdown

| Timestamp | Visual Cue | Segment Topic |
| :--- | :--- | :--- |
| **0:00 – 0:35** | Show `output/CHARTS_README.md` | Introduction & Core Principles of Business Visualization |
| **0:35 – 1:15** | Open `chart1_revenue_by_product.png` | Chart 1: Bar Chart (Comparison across Categories) |
| **1:15 – 1:55** | Open `chart2_revenue_trend.png` | Chart 2: Multi-Series Line Chart (Time-Series Trends) |
| **1:55 – 2:35** | Open `chart3_order_value_distribution.png` | Chart 3: Histogram & KDE (Revealing Hidden Distributions) |
| **2:35 – 3:15** | Open `chart4_revenue_composition.png` | Chart 4: Stacked Bar Chart (Part-to-Whole Composition) |
| **3:15 – 3:55** | Open `chart5_marketing_vs_revenue.png` | Chart 5: Scatter Plot & Regression (Correlation & Outliers) |
| **3:55 – 4:30** | Show `assignment-35-visualizations.py` | Design System, Accessibility & Conclusion |

---

## 🎙️ Spoken Script (Word-for-Word Guide)

### 1. Introduction (0:00 – 0:35)
> *"Hello everyone! Today, I am presenting our work on **Business Visualisation Principles**.*
>
> *In business analytics, data only creates value when stakeholders can interpret it in seconds without misinterpretation. Charts fail when the wrong visual encoding is used—like using a pie chart for time-series data or a line chart for discrete categories.*
>
> *In this project, we built a suite of five production-grade visualizations, matching every data relationship to its ideal chart type, applying complete human-readable labeling, maintaining an accessible color palette, and spotlighting critical business insights through annotations."*

---

### 2. Chart 1: Categorical Comparison with Bar Chart (0:35 – 1:15)
*(Show `output/chart1_revenue_by_product.png`)*

> *"Our **First Chart** answers: 'Which product line generated the most revenue in Q4?'*
>
> *We chose a **Horizontal Bar Chart** because the human eye effortlessly compares bar lengths, and horizontal bars accommodate long category labels without awkward text angling.*
> * *Notice the **complete labeling**: revenue is formatted cleanly in millions on the X-axis (`$1.0M`, `$2.0M`), and each bar displays its exact value directly.*
> * *We added a green dashed **$2.5M Target Benchmark** line and annotated our top performer—**AI & ML Services at $3.45M**, which alone drove **30.5% of total Q4 revenue**."*

---

### 3. Chart 2: Time-Series Trends with Line Chart (1:15 – 1:55)
*(Show `output/chart2_revenue_trend.png`)*

> *"Our **Second Chart** tracks revenue trends over the 12 months of 2024 across our top 3 products.*
>
> *A **Line Chart** is the correct choice here because the continuous connected lines convey temporal continuity.*
> * *To ensure clarity, each product line uses a distinct marker shape—circles, squares, and triangles—so viewers don't have to rely on color alone.*
> * *We highlighted two crucial events using annotations: the **August seasonal dip** caused by enterprise summer budget pauses, and the record-setting **December peak of $420K**."*

---

### 4. Chart 3: Distribution Analysis with Histogram (1:55 – 2:35)
*(Show `output/chart3_order_value_distribution.png`)*

> *"Our **Third Chart** investigates transaction order value distributions.*
>
> *A common business mistake is relying solely on simple averages. By plotting a **Histogram with a Kernel Density Estimation (KDE) curve**, we uncover a clear **bimodal distribution**.*
> * *The chart immediately reveals two distinct customer segments: a large Self-Serve SMB cluster peaking around **$120**, and an Enterprise bulk contract cluster peaking around **$650**.*
> * *We annotated both peaks alongside our Mean ($305) and Median ($180) reference lines, giving leadership the context needed for tiered pricing strategies."*

---

### 5. Chart 4: Composition over Time with Stacked Bar (2:35 – 3:15)
*(Show `output/chart4_revenue_composition.png`)*

> *"Our **Fourth Chart** answers: 'How is our quarterly revenue mix shifting across product lines?'*
>
> *We utilized a **Stacked Bar Chart** to show both the overall quarterly revenue total and the internal product composition simultaneously.*
> * *Total revenue values are displayed at the top of each bar—growing from $7.10M in Q1 to $10.05M in Q4.*
> * *Our annotation points out the strategic narrative: an explosive **+91.6% YoY surge in AI & ML Services**, illustrating how our product mix is shifting toward high-margin AI offerings."*

---

### 6. Chart 5: Correlation & Outlier Analysis with Scatter Plot (3:15 – 3:55)
*(Show `output/chart5_marketing_vs_revenue.png`)*

> *"Our **Fifth Chart** examines the relationship between regional marketing campaign spend and generated revenue.*
>
> *A **Scatter Plot with an Ordinary Least Squares Trendline** is ideal for bivariate correlation analysis.*
> * *The fitted trendline confirms a **strong positive correlation ($r = 0.84$)**, demonstrating that marketing investment consistently converts to top-line growth.*
> * *Crucially, we annotated a severe **campaign outlier** at $112K spend that only generated $1.25M in revenue—allowing the marketing team to quickly investigate a delayed regional launch."*

---

### 7. Accessibility, Color Palette & Conclusion (3:55 – 4:30)
*(Show `assignment-35-visualizations.py` palette definition)*

> *"Across all five charts, we applied a single unified design system:*
> * *We defined an accessible color palette with primary steel blue, secondary amber, and high-contrast alert tones.*
> * *To support the 8% of individuals with color vision deficiency, we paired colors with unique marker glyphs, dashed line styles, and direct value annotations.*
>
> *All 5 charts have been exported as high-resolution 300 DPI PNGs in our `output/` directory alongside full documentation in `CHARTS_README.md`.*
>
> *Thank you for watching!"*
