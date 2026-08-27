"""
Interactive Plotly Visualizations & Metric Switchers
====================================================
Tasks:
- Task 1: Create Two Plotly Charts with Hover Tooltips (Revenue Trend & Product Performance)
- Task 2: Create Dropdown Filter to Toggle Views without Page Reload (updatemenus)
- Task 3: Enable Zoom, Pan, Box/Lasso Select, and Reset Interactions
- Task 4: Streamlit Integration (streamlit_plotly_app.py)
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine

# Output directories
OUTPUT_DIR = "output_plotly"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("frontend/public", exist_ok=True)

# -----------------------------------------------------------------------------
# 1. SYNTHETIC DATABASE SETUP
# -----------------------------------------------------------------------------
DB_FILE = "plotly_analytics.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

def setup_database():
    """Generates realistic e-commerce order & product performance data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        base_price REAL,
        cost_price REAL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        order_date TEXT,
        quantity INTEGER,
        amount REAL,
        profit REAL,
        customer_segment TEXT
    );
    """)

    # Seed products
    products = [
        (1, 'Enterprise Cloud Suite', 'Software', 1200.0, 350.0),
        (2, 'Developer Pro Toolset', 'Software', 450.0, 120.0),
        (3, 'AI Analytics Engine', 'AI/ML', 850.0, 220.0),
        (4, 'Cybersecurity Shield', 'Security', 650.0, 180.0),
        (5, 'Data Pipeline Connector', 'Data', 320.0, 80.0),
        (6, 'Team Collaboration Hub', 'Software', 250.0, 60.0),
        (7, 'API Gateway Sentinel', 'Infrastructure', 550.0, 140.0),
        (8, 'Storage Optimizer', 'Infrastructure', 180.0, 45.0)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)

    # Seed 5,000 orders over 90 days
    np.random.seed(42)
    start_date = pd.Timestamp("2026-06-01")
    orders_data = []
    segments = ['Enterprise', 'Mid-Market', 'SMB', 'Startup']
    segment_weights = [0.35, 0.30, 0.20, 0.15]

    for i in range(1, 5001):
        rand_day = np.random.randint(0, 90)
        order_dt = (start_date + pd.Timedelta(days=rand_day)).strftime('%Y-%m-%d')
        prod = products[np.random.randint(0, len(products))]
        qty = np.random.choice([1, 2, 3, 5, 10], p=[0.55, 0.25, 0.10, 0.07, 0.03])
        amt = prod[3] * qty * np.random.uniform(0.92, 1.05) # slight discount/pricing variance
        profit = amt - (prod[4] * qty)
        seg = np.random.choice(segments, p=segment_weights)

        orders_data.append((i, np.random.randint(101, 1500), prod[0], order_dt, qty, round(amt, 2), round(profit, 2), seg))

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", orders_data)
    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
# 2. TASK 1: CREATE TWO PLOTLY CHARTS WITH HOVER TOOLTIPS
# -----------------------------------------------------------------------------
def create_task1_chart1():
    """
    Chart 1 - Daily Revenue Trend with Custom Unified Hover
    - Unified hover template with date formatting
    - Revenue in currency format ($)
    - Order counts and 7-day rolling average
    """
    df = pd.read_sql("""
        SELECT 
            DATE(order_date) as date,
            SUM(amount) as revenue,
            COUNT(order_id) as order_count,
            AVG(amount) as avg_order_value
        FROM orders
        GROUP BY DATE(order_date)
        ORDER BY DATE(order_date)
    """, engine)

    # Calculate 7-day rolling average
    df['rolling_revenue'] = df['revenue'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    # Trace 1: Daily Revenue with Markers
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>' +
                      'Daily Revenue: $%{y:,.2f}<br>' +
                      'Completed Orders: %{customdata[0]:,}<br>' +
                      'Avg Order Value: $%{customdata[1]:.2f}<extra></extra>',
        customdata=df[['order_count', 'avg_order_value']],
        line=dict(color='#38bdf8', width=2.5),
        marker=dict(size=6, color='#0284c7', symbol='circle')
    ))

    # Trace 2: 7-Day Moving Average
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['rolling_revenue'],
        mode='lines',
        name='7-Day Rolling Trend',
        hovertemplate='7-Day Trend: $%{y:,.2f}<extra></extra>',
        line=dict(color='#f59e0b', width=2, dash='dot')
    ))

    fig.update_layout(
        title=dict(
            text='<b>Daily Revenue Trend & Rolling Average</b><br><span style="font-size:12px;color:#94a3b8">Interactive time-series with unified hover tooltips</span>',
            x=0.05,
            xanchor='left'
        ),
        xaxis=dict(
            title='Order Date',
            gridcolor='#1e293b',
            showgrid=True,
            rangeslider=dict(visible=True, thickness=0.08)
        ),
        yaxis=dict(
            title='Total Revenue ($)',
            gridcolor='#1e293b',
            showgrid=True,
            tickprefix='$',
            tickformat=',.0f'
        ),
        hovermode='x unified',
        template='plotly_dark',
        height=520,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    # Save outputs
    fig.write_html('chart1_revenue_trend.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart1_revenue_trend.html'))
    fig.write_html('frontend/public/chart1_revenue_trend.html')
    print("✅ Created Chart 1: chart1_revenue_trend.html")
    return fig


def create_task1_chart2():
    """
    Chart 2 - Product Performance with Multi-Column Hover
    - Horizontal ranked bar chart
    - 5+ data fields in hover (Product, Category, Revenue, Orders, AOV, Gross Margin %)
    """
    df = pd.read_sql("""
        SELECT 
            p.product_name,
            p.category,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as total_orders,
            AVG(o.amount) as avg_order_value,
            SUM(o.profit) as total_profit,
            (SUM(o.profit) * 100.0 / SUM(o.amount)) as profit_margin_pct
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue ASC
    """, engine)

    # Color scale by category
    category_colors = {
        'Software': '#38bdf8',
        'AI/ML': '#a855f7',
        'Security': '#10b981',
        'Data': '#f59e0b',
        'Infrastructure': '#ec4899'
    }
    bar_colors = [category_colors.get(c, '#64748b') for c in df['category']]

    fig = go.Figure(data=go.Bar(
        x=df['total_revenue'],
        y=df['product_name'],
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='#ffffff', width=1)
        ),
        customdata=df[['category', 'total_orders', 'avg_order_value', 'total_profit', 'profit_margin_pct']],
        hovertemplate=(
            '<b>%{y}</b><br>' +
            'Category: %{customdata[0]}<br>' +
            'Total Revenue: $%{x:,.2f}<br>' +
            'Orders Count: %{customdata[1]:,}<br>' +
            'Avg Order Value: $%{customdata[2]:,.2f}<br>' +
            'Gross Profit: $%{customdata[3]:,.2f}<br>' +
            'Profit Margin: %{customdata[4]:.1f}%<br>' +
            '<extra></extra>'
        )
    ))

    fig.update_layout(
        title=dict(
            text='<b>Product Performance Ranking</b><br><span style="font-size:12px;color:#94a3b8">Multi-column hover showing Revenue, Volume, AOV & Margin %</span>',
            x=0.05,
            xanchor='left'
        ),
        xaxis=dict(
            title='Total Revenue ($)',
            gridcolor='#1e293b',
            tickprefix='$',
            tickformat=',.0f'
        ),
        yaxis=dict(
            title='',
            gridcolor='#1e293b'
        ),
        template='plotly_dark',
        height=520,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b',
        hoverlabel=dict(
            bgcolor='#1e293b',
            font_size=13,
            font_family='Inter, sans-serif'
        )
    )

    # Save outputs
    fig.write_html('chart2_product_performance.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart2_product_performance.html'))
    fig.write_html('frontend/public/chart2_product_performance.html')
    print("✅ Created Chart 2: chart2_product_performance.html")
    return fig

# -----------------------------------------------------------------------------
# 3. TASK 2: CREATE DROPDOWN FILTER TO TOGGLE VIEWS (UPDATEMENUS)
# -----------------------------------------------------------------------------
def create_task2_dropdown_chart():
    """
    Chart 3 - Product Performance with Dropdown Filter
    - Client-side switcher between Revenue, Profit, and Order Count
    - Zero page reload / Zero database roundtrip
    """
    df = pd.read_sql("""
        SELECT 
            p.product_name,
            SUM(o.amount) as revenue,
            SUM(o.profit) as profit,
            COUNT(o.order_id) as order_count
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY revenue DESC
    """, engine)

    products = df['product_name'].tolist()
    revenue_data = df['revenue'].tolist()
    profit_data = df['profit'].tolist()
    order_data = df['order_count'].tolist()

    fig = go.Figure()

    # Trace 0: Revenue (Default Visible)
    fig.add_trace(go.Bar(
        x=products,
        y=revenue_data,
        name='Revenue ($)',
        marker=dict(color='#38bdf8'),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
        visible=True
    ))

    # Trace 1: Profit (Initially Hidden)
    fig.add_trace(go.Bar(
        x=products,
        y=profit_data,
        name='Gross Profit ($)',
        marker=dict(color='#10b981'),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>',
        visible=False
    ))

    # Trace 2: Order Count (Initially Hidden)
    fig.add_trace(go.Bar(
        x=products,
        y=order_data,
        name='Order Volume (Count)',
        marker=dict(color='#f59e0b'),
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>',
        visible=False
    ))

    # Configure Dropdown updatemenus
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.0,
                xanchor="left",
                y=1.18,
                yanchor="top",
                active=0,
                bgcolor="#1e293b",
                bordercolor="#475569",
                font=dict(color="#ffffff", size=12),
                buttons=[
                    dict(
                        label="💰 Metric: Total Revenue ($)",
                        method="update",
                        args=[
                            {"visible": [True, False, False]},
                            {"title": "<b>Product Performance — Total Revenue ($)</b>",
                             "yaxis": {"title": "Revenue ($)", "tickprefix": "$", "tickformat": ",.0f", "gridcolor": "#1e293b"}}
                        ]
                    ),
                    dict(
                        label="📈 Metric: Gross Profit ($)",
                        method="update",
                        args=[
                            {"visible": [False, True, False]},
                            {"title": "<b>Product Performance — Gross Profit ($)</b>",
                             "yaxis": {"title": "Gross Profit ($)", "tickprefix": "$", "tickformat": ",.0f", "gridcolor": "#1e293b"}}
                        ]
                    ),
                    dict(
                        label="📦 Metric: Order Volume (Count)",
                        method="update",
                        args=[
                            {"visible": [False, False, True]},
                            {"title": "<b>Product Performance — Order Volume (Count)</b>",
                             "yaxis": {"title": "Completed Orders (Count)", "tickprefix": "", "tickformat": ",.0f", "gridcolor": "#1e293b"}}
                        ]
                    )
                ]
            )
        ],
        title=dict(
            text='<b>Product Performance — Total Revenue ($)</b>',
            x=0.28,
            xanchor='left'
        ),
        xaxis=dict(title='Product Name', gridcolor='#1e293b', tickangle=-20),
        yaxis=dict(title='Revenue ($)', gridcolor='#1e293b', tickprefix='$', tickformat=',.0f'),
        template='plotly_dark',
        height=540,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b'
    )

    # Save outputs
    fig.write_html('chart3_metric_selector.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart3_metric_selector.html'))
    fig.write_html('frontend/public/chart3_metric_selector.html')
    print("✅ Created Chart 3: chart3_metric_selector.html")
    return fig

# -----------------------------------------------------------------------------
# 4. TASK 3: ENABLE ZOOM, PAN, AND RESET INTERACTIONS
# -----------------------------------------------------------------------------
def create_task3_interactive_chart():
    """
    Chart 4 - Multi-Dimensional Order Explorer with Native Plotly Controls
    - Zoom: Click and drag box
    - Pan: Shift + Click + Drag
    - Reset: Double-Click
    - Box & Lasso Select: Isolate subsets
    """
    df = pd.read_sql("""
        SELECT 
            o.order_id,
            o.order_date,
            o.amount,
            o.profit,
            o.quantity,
            o.customer_segment,
            p.product_name,
            p.category
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        LIMIT 1000
    """, engine)

    color_map = {
        'Enterprise': '#38bdf8',
        'Mid-Market': '#10b981',
        'SMB': '#f59e0b',
        'Startup': '#ec4899'
    }

    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0.0)

    fig = go.Figure()

    for segment, seg_df in df.groupby('customer_segment'):
        sizes = (seg_df['quantity'].astype(float) * 3.5 + 5.0).tolist()
        fig.add_trace(go.Scatter(
            x=seg_df['amount'],
            y=seg_df['profit'],
            mode='markers',
            name=str(segment),
            marker=dict(
                size=sizes,
                color=color_map.get(segment, '#94a3b8'),
                opacity=0.85,
                line=dict(width=1, color='#ffffff')
            ),
            customdata=seg_df[['product_name', 'category', 'quantity', 'order_date']],
            hovertemplate=(
                '<b>%{customdata[0]}</b> (%{customdata[1]})<br>' +
                'Order Amount: $%{x:,.2f}<br>' +
                'Gross Profit: $%{y:,.2f}<br>' +
                'Quantity: %{customdata[2]}<br>' +
                'Segment: ' + segment + '<br>' +
                'Date: %{customdata[3]}<extra></extra>'
            )
        ))

    fig.update_layout(
        title=dict(
            text='<b>Order Amount vs Profitability Explorer</b><br><span style="font-size:12px;color:#94a3b8">Interactive exploration with Zoom, Pan, Lasso Select, and Double-Click Reset</span>',
            x=0.05,
            xanchor='left'
        ),
        dragmode='zoom',
        hovermode='closest',
        xaxis=dict(title='Order Amount ($)', gridcolor='#1e293b', tickprefix='$'),
        yaxis=dict(title='Gross Profit ($)', gridcolor='#1e293b', tickprefix='$'),
        template='plotly_dark',
        height=560,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b',
        legend=dict(title='Customer Segment', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        modebar=dict(
            bgcolor='#1e293b',
            color='#94a3b8',
            activecolor='#38bdf8'
        )
    )

    # Save outputs
    fig.write_html('chart4_interactive.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart4_interactive.html'))
    fig.write_html('frontend/public/chart4_interactive.html')
    print("✅ Created Chart 4: chart4_interactive.html")
    return fig

# -----------------------------------------------------------------------------
# 5. MASTER RUNNER & VALIDATION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING INTERACTIVE PLOTLY VISUALIZATIONS (TASKS 1 - 3)")
    print("=" * 70)
    setup_database()
    create_task1_chart1()
    create_task1_chart2()
    create_task2_dropdown_chart()
    create_task3_interactive_chart()
    print("=" * 70)
    print("🎉 ALL 4 PLOTLY CHARTS CREATED SUCCESSFULLY!")
    print("Output Files:")
    print("  1. chart1_revenue_trend.html (Daily Revenue with Unified Tooltip)")
    print("  2. chart2_product_performance.html (Product Ranking with Multi-Column Hover)")
    print("  3. chart3_metric_selector.html (Dropdown Metric Toggle - Zero Reload)")
    print("  4. chart4_interactive.html (Zoom / Pan / Lasso / Reset Explorer)")
    print("=" * 70)
