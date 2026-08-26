"""
Assignment 2.45: Business Visualisation Principles
Script: assignment-35-visualizations.py

Generates 5 distinct, production-grade business visualizations:
1. Horizontal Bar Chart: Q4 Revenue by Product Line (Comparison)
2. Multi-Series Line Chart: 12-Month Revenue Trend for Top Products (Trend)
3. Histogram & KDE: Distribution of Transaction Order Values (Distribution)
4. Stacked Bar Chart: Quarterly Revenue Composition by Product (Composition)
5. Scatter Plot & Regression Line: Marketing Spend vs. Revenue Generated (Correlation)

Includes:
- Complete labeling (Titles, Axis units, Legends, Value labels)
- Consistent, accessible color palette
- Actionable insight annotations and reference threshold lines
- 300 DPI high-resolution PNG exports in output/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# ==============================================================================
# 🎨 1. GLOBAL DESIGN SYSTEM & ACCESSIBLE COLOR PALETTE (TASK 3)
# ==============================================================================
PALETTE = {
    'primary': '#1f77b4',     # Steel Blue - Dominant metric / Primary series
    'secondary': '#ff7f0e',   # Warm Amber - Secondary comparison / Emerging series
    'success': '#2ca02c',     # Forest Green - Targets, positive growth, benchmarks
    'danger': '#d62728',      # Crimson Red - Anomalies, outliers, critical alerts
    'purple': '#9467bd',      # Deep Violet - Supplementary category
    'neutral': '#7f7f7f',     # Slate Gray - Grids, borders, baseline references
    'light_bg': '#f8f9fa',    # Background card fill
    'annotation_bg': '#fff3cd'# Light Gold annotation callout box
}

# Categorical color cycle for multi-series charts (Color-blind safe contrasts)
CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#e377c2']

# Apply cohesive Matplotlib rcParams styling
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'figure.titlesize': 15,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.facecolor': '#ffffff',
    'axes.facecolor': '#fafbfc',
    'axes.edgecolor': '#cccccc',
    'axes.grid': True,
    'grid.color': '#e1e4e8',
    'grid.linestyle': '--',
    'grid.alpha': 0.6
})

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# 📊 2. CHART GENERATION FUNCTIONS (TASKS 1, 2, 3, 4)
# ==============================================================================

def create_chart_1_bar():
    """
    Chart 1: Horizontal Bar Chart - Q4 Revenue by Product Line (Comparison)
    Answers: Which product line generated the highest revenue in Q4?
    """
    print("Generating Chart 1: Revenue by Product Line (Bar Chart)...")
    
    # Dataset: Q4 Revenue by Product Category
    data = {
        'Product Line': ['AI & ML Services', 'Cloud Infrastructure', 'Developer Tools', 'Security Suite', 'Analytics Platform'],
        'Revenue': [3450000, 2850000, 2100000, 1650000, 1250000]
    }
    df = pd.DataFrame(data).sort_values(by='Revenue', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Horizontal Bar Plot
    bars = ax.barh(df['Product Line'], df['Revenue'], color=PALETTE['primary'], height=0.6, edgecolor='none')

    # Data Labels on each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 60000, 
            bar.get_y() + bar.get_height() / 2, 
            f"${width/1e6:.2f}M", 
            va='center', 
            ha='left', 
            fontsize=10, 
            fontweight='bold',
            color='#24292e'
        )

    # Reference Line: Quarterly Target Benchmark ($2.5M)
    target_val = 2500000
    ax.axvline(x=target_val, color=PALETTE['success'], linestyle='--', linewidth=2, label=f'Q4 Target ($2.5M)')

    # Annotation: Top Performer Insight
    ax.annotate(
        'Top Performer\n(30.5% of Total Q4 Revenue)',
        xy=(3450000, 4), # AI & ML Services position
        xytext=(2600000, 3.2),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Formatting & Labels
    ax.set_title('Q4 Total Revenue by Product Line (Comparison)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Revenue ($ in Millions)', fontsize=12, labelpad=10)
    ax.set_ylabel('Product Line', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    ax.set_xlim(0, 4200000)
    ax.legend(loc='lower right', framealpha=0.95)

    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, 'chart1_revenue_by_product.png')
    plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✔ Chart 1 saved to {chart1_path}")


def create_chart_2_line():
    """
    Chart 2: Multi-Series Line Chart - 12-Month Revenue Trend for Top 3 Products (Trend)
    Answers: How has monthly revenue trended across top product lines throughout 2024?
    """
    print("Generating Chart 2: Revenue Trend over 12 Months (Line Chart)...")

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    np.random.seed(42)

    # Simulated 12-month trajectory with seasonal August dip and Q4 surge
    ai_ml_rev = [210, 225, 240, 260, 290, 310, 305, 235, 320, 350, 385, 420] # in Thousands
    cloud_rev = [280, 285, 295, 300, 305, 310, 290, 220, 305, 315, 330, 345]
    dev_tools = [180, 190, 195, 205, 215, 220, 210, 175, 225, 235, 250, 265]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Multi-series line plotting with distinct markers and styles
    ax.plot(months, ai_ml_rev, marker='o', linewidth=2.5, color=PALETTE['primary'], label='AI & ML Services')
    ax.plot(months, cloud_rev, marker='s', linewidth=2.5, color=PALETTE['secondary'], label='Cloud Infrastructure')
    ax.plot(months, dev_tools, marker='^', linewidth=2.5, color=PALETTE['purple'], label='Developer Tools')

    # Reference Line: Monthly Portfolio Baseline
    ax.axhline(y=300, color=PALETTE['neutral'], linestyle=':', linewidth=1.5, label='Tier 1 Revenue Threshold ($300K)')

    # Annotation 1: Summer Seasonality Dip in August
    aug_idx = months.index('Aug')
    ax.annotate(
        'Summer Seasonality Dip\n(August enterprise budget pause)',
        xy=(aug_idx, 235),
        xytext=(aug_idx, 150),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Annotation 2: Q4 Year-End Peak
    dec_idx = months.index('Dec')
    ax.annotate(
        'Year-End Peak\n($420K Record)',
        xy=(dec_idx, 420),
        xytext=(dec_idx - 1.2, 435),
        arrowprops=dict(arrowstyle='->', color=PALETTE['success'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#d4edda', edgecolor='#c3e6cb', alpha=0.9)
    )

    # Formatting & Labels
    ax.set_title('2024 Monthly Revenue Trend Across Top 3 Products (Time-Series)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Month (Fiscal Year 2024)', fontsize=12, labelpad=10)
    ax.set_ylabel('Monthly Revenue ($ in Thousands)', fontsize=12, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.0f}K'))
    ax.set_ylim(120, 480)
    ax.legend(loc='upper left', framealpha=0.95)

    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_DIR, 'chart2_revenue_trend.png')
    plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✔ Chart 2 saved to {chart2_path}")


def create_chart_3_histogram():
    """
    Chart 3: Histogram with KDE - Distribution of Transaction Order Values (Distribution)
    Answers: What is the distribution of transaction sizes and what are the typical customer spending clusters?
    """
    print("Generating Chart 3: Order Value Distribution (Histogram)...")

    np.random.seed(42)
    # Bimodal order distribution: Tier 1 self-serve ($100 mean) & Tier 2 enterprise ($650 mean)
    tier1_orders = np.random.normal(loc=120, scale=35, size=3500)
    tier2_orders = np.random.normal(loc=650, scale=120, size=1500)
    all_order_values = np.clip(np.concatenate([tier1_orders, tier2_orders]), 20, 1200)

    fig, ax = plt.subplots(figsize=(11, 6))

    # Histogram + KDE Distribution
    sns.histplot(
        all_order_values, 
        bins=40, 
        kde=True, 
        color=PALETTE['primary'], 
        edgecolor='#ffffff', 
        linewidth=1.2, 
        ax=ax,
        line_kws={'linewidth': 2.2, 'color': PALETTE['secondary']}
    )

    # Summary Statistics lines
    mean_val = np.mean(all_order_values)
    median_val = np.median(all_order_values)
    ax.axvline(mean_val, color=PALETTE['danger'], linestyle='--', linewidth=2, label=f'Mean Order: ${mean_val:.0f}')
    ax.axvline(median_val, color=PALETTE['success'], linestyle=':', linewidth=2, label=f'Median Order: ${median_val:.0f}')

    # Annotation 1: Peak 1 (SMB / Self-Serve Tier)
    ax.annotate(
        'Cluster 1: Self-Serve Tier\n(Peak around $120)',
        xy=(120, 380),
        xytext=(220, 430),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Annotation 2: Peak 2 (Enterprise Bulk Tier)
    ax.annotate(
        'Cluster 2: Enterprise Tier\n(Peak around $650)',
        xy=(650, 95),
        xytext=(800, 200),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Formatting & Labels
    ax.set_title('Distribution of Transaction Order Values (Bimodal Population)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Order Value ($ USD)', fontsize=12, labelpad=10)
    ax.set_ylabel('Transaction Frequency (Count)', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}'))
    ax.set_xlim(0, 1100)
    ax.legend(loc='upper right', framealpha=0.95)

    plt.tight_layout()
    chart3_path = os.path.join(OUTPUT_DIR, 'chart3_order_value_distribution.png')
    plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✔ Chart 3 saved to {chart3_path}")


def create_chart_4_stacked_bar():
    """
    Chart 4: Stacked Bar Chart - Quarterly Revenue Composition by Product Line (Composition)
    Answers: How does quarterly revenue break down by product line, and how is portfolio composition evolving?
    """
    print("Generating Chart 4: Revenue Composition by Quarter (Stacked Bar)...")

    quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
    categories = ['AI & ML Services', 'Cloud Infrastructure', 'Developer Tools', 'Security Suite']
    
    # Revenue data ($ in Millions)
    ai_ml = np.array([1.8, 2.2, 2.7, 3.45])
    cloud = np.array([2.5, 2.6, 2.7, 2.85])
    dev   = np.array([1.6, 1.7, 1.9, 2.10])
    sec   = np.array([1.2, 1.3, 1.5, 1.65])
    
    totals = ai_ml + cloud + dev + sec

    fig, ax = plt.subplots(figsize=(11, 6.5))

    width = 0.55
    b1 = ax.bar(quarters, ai_ml, width=width, label='AI & ML Services', color=CHART_COLORS[0])
    b2 = ax.bar(quarters, cloud, bottom=ai_ml, width=width, label='Cloud Infrastructure', color=CHART_COLORS[1])
    b3 = ax.bar(quarters, dev, bottom=ai_ml + cloud, width=width, label='Developer Tools', color=CHART_COLORS[2])
    b4 = ax.bar(quarters, sec, bottom=ai_ml + cloud + dev, width=width, label='Security Suite', color=CHART_COLORS[3])

    # Display total revenue on top of each stacked bar
    for idx, total in enumerate(totals):
        ax.text(
            idx, 
            total + 0.18, 
            f"${total:.2f}M", 
            ha='center', 
            va='bottom', 
            fontsize=11, 
            fontweight='bold',
            color='#1a1a1a'
        )

    # Annotation: Compositional Growth Shift
    ax.annotate(
        'Portfolio Shift:\nAI/ML Surge (+91.6% YoY Growth)',
        xy=(3, 1.7), # Center of Q4 AI & ML block
        xytext=(2.1, 4.5),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Formatting & Labels
    ax.set_title('Quarterly Revenue Composition by Product Line (2024 Fiscal Year)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Fiscal Quarter', fontsize=12, labelpad=10)
    ax.set_ylabel('Total Revenue ($ in Millions)', fontsize=12, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.1f}M'))
    ax.set_ylim(0, 11.5)
    ax.legend(loc='upper left', framealpha=0.95, title='Product Line')

    plt.tight_layout()
    chart4_path = os.path.join(OUTPUT_DIR, 'chart4_revenue_composition.png')
    plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✔ Chart 4 saved to {chart4_path}")


def create_chart_5_scatter():
    """
    Chart 5: Scatter Plot with Regression Trendline - Marketing Spend vs Revenue (Correlation)
    Answers: Is there a statistically significant correlation between regional marketing spend and generated revenue?
    """
    print("Generating Chart 5: Marketing Spend vs. Revenue (Scatter Plot)...")

    np.random.seed(42)
    # Generate 50 regional campaign points with strong positive correlation
    spend = np.random.uniform(15, 120, size=50) # Spend in $ Thousands
    noise = np.random.normal(0, 0.45, size=50)
    revenue = 0.035 * spend + 0.5 + noise       # Revenue in $ Millions
    revenue = np.clip(revenue, 0.5, 5.0)

    # Add one deliberate outlier (High spend $110K, Low revenue $1.2M due to regional channel delivery failure)
    spend[12] = 112.0
    revenue[12] = 1.25

    fig, ax = plt.subplots(figsize=(11, 6.5))

    # Scatter plot
    ax.scatter(
        spend, 
        revenue, 
        color=PALETTE['primary'], 
        edgecolor='#ffffff', 
        s=85, 
        alpha=0.85, 
        zorder=3,
        label='Regional Marketing Campaigns'
    )

    # Fit Linear Regression Line (excluding outlier for robust fit)
    mask = np.ones(len(spend), dtype=bool)
    mask[12] = False
    slope, intercept = np.polyfit(spend[mask], revenue[mask], 1)
    x_vals = np.linspace(10, 125, 100)
    y_vals = slope * x_vals + intercept
    
    corr_coef = np.corrcoef(spend[mask], revenue[mask])[0, 1]

    ax.plot(
        x_vals, 
        y_vals, 
        color=PALETTE['danger'], 
        linestyle='-', 
        linewidth=2.2, 
        zorder=2,
        label=f'Trendline (r = {corr_coef:.2f}, Strong Correlation)'
    )

    # Annotation 1: Outlier Identification
    ax.annotate(
        'Campaign Outlier:\nHigh Spend ($112K) with Low Return ($1.25M)\n[Delayed Channel Launch]',
        xy=(112.0, 1.25),
        xytext=(80, 0.75),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=1.8),
        fontsize=9.5,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['annotation_bg'], edgecolor='#ffeeba', alpha=0.9)
    )

    # Annotation 2: High Efficiency Cluster
    ax.annotate(
        'High ROI Cluster\n(Spend > $90K drives $4M+ Revenue)',
        xy=(98, 4.2),
        xytext=(60, 4.6),
        arrowprops=dict(arrowstyle='->', color=PALETTE['success'], lw=1.8),
        fontsize=9.5,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#d4edda', edgecolor='#c3e6cb', alpha=0.9)
    )

    # Formatting & Labels
    ax.set_title('Correlation Analysis: Marketing Campaign Spend vs. Generated Revenue', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Marketing Campaign Spend ($ in Thousands)', fontsize=12, labelpad=10)
    ax.set_ylabel('Revenue Generated ($ in Millions)', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}K'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'${y:.1f}M'))
    ax.set_xlim(5, 130)
    ax.set_ylim(0.4, 5.2)
    ax.legend(loc='upper left', framealpha=0.95)

    plt.tight_layout()
    chart5_path = os.path.join(OUTPUT_DIR, 'chart5_marketing_vs_revenue.png')
    plt.savefig(chart5_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✔ Chart 5 saved to {chart5_path}")


def main():
    print("=" * 80)
    print("STARTING ASSIGNMENT 2.45: BUSINESS VISUALISATION PRINCIPLES")
    print("=" * 80)
    
    create_chart_1_bar()
    create_chart_2_line()
    create_chart_3_histogram()
    create_chart_4_stacked_bar()
    create_chart_5_scatter()

    print("=" * 80)
    print("ALL 5 VISUALIZATIONS GENERATED AND EXPORTED SUCCESSFULLY AT 300 DPI!")
    print(f"Directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
