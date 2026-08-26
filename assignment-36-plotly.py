"""
Assignment: Interactive Plotly Chart Design
Script: assignment-36-plotly.py

Fulfills:
- Task 1: Two Plotly Charts with rich, multi-column hover tooltips (chart1_revenue_trend.html, chart2_product_performance.html)
- Task 2: Dropdown filter for instant metric switching without page reloads (chart3_metric_selector.html)
- Task 3: Native Plotly interactive controls: Zoom, Pan, Box/Lasso Select, Double-click Reset (chart4_interactive.html)
- Task 4: Streamlit integration readiness & standalone HTML generation
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

def get_db_connection(db_path: str = "data_layer.db"):
    """Returns database connection to data_layer.db."""
    return sqlite3.connect(db_path)

# ==============================================================================
# 📊 TASK 1: CREATE TWO PLOTLY CHARTS WITH HOVER TOOLTIPS
# ==============================================================================

def create_chart_1_revenue_trend(conn):
    """
    Chart 1: Daily Revenue Trend with Custom Unified Hover Tooltip.
    Displays formatted date, daily revenue, and completed order count.
    """
    print("Generating Chart 1: Daily Revenue Trend with Custom Hover...")
    
    query = """
    SELECT 
        DATE(order_date) AS date, 
        SUM(order_amount) AS revenue, 
        COUNT(*) AS order_count,
        ROUND(AVG(order_amount), 2) AS avg_order_value
    FROM orders
    WHERE status = 'Completed'
    GROUP BY DATE(order_date)
    ORDER BY DATE(order_date);
    """
    df = pd.read_sql(query, conn)
    df['custom_info'] = df.apply(
        lambda r: f"Date: <b>{r['date']}</b><br>Daily Revenue: <b>${r['revenue']:,.2f}</b><br>Orders Placed: <b>{r['order_count']:,}</b><br>Avg Order Value: <b>${r['avg_order_value']:,.2f}</b>", 
        axis=1
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        customdata=df[['order_count', 'avg_order_value']],
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                      'Daily Revenue: <b>$%{y:,.2f}</b><br>' +
                      'Completed Orders: <b>%{customdata[0]:,}</b><br>' +
                      'Avg Order Value: <b>$%{customdata[1]:,.2f}</b><br>' +
                      '<extra></extra>',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=6, color='#1f77b4', symbol='circle')
    ))

    # Add 7-day rolling average trendline
    df['rolling_7d'] = df['revenue'].rolling(window=7, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['rolling_7d'],
        mode='lines',
        name='7-Day Moving Avg',
        line=dict(color='#ff7f0e', width=2, dash='dot'),
        hovertemplate='<b>7-Day Avg:</b> $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text='<b>Daily Revenue Trend with Custom Hover Tooltips</b><br><sup>Interactive time-series analysis (Fiscal Year 2024)</sup>',
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='#e1e4e8',
            rangeslider=dict(visible=True)
        ),
        yaxis=dict(
            title='Revenue ($ USD)',
            showgrid=True,
            gridcolor='#e1e4e8',
            tickprefix='$',
            tickformat=',.0f'
        ),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='sans-serif'),
        plot_bgcolor='#fafbfc',
        paper_bgcolor='#ffffff',
        height=550,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    # Save HTML to root and output directory
    fig.write_html('chart1_revenue_trend.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart1_revenue_trend.html'))
    print("✔ Chart 1 saved: chart1_revenue_trend.html")
    return fig


def create_chart_2_product_performance(conn):
    """
    Chart 2: Product Performance with Multi-Column Hover.
    Displays Top 15 Products with 4 hover fields (Revenue, Order Count, AOV, Gross Margin %).
    """
    print("Generating Chart 2: Product Performance with Multi-Column Hover...")

    query = """
    SELECT 
        p.product_name,
        p.category,
        ROUND(SUM(o.order_amount), 2) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(AVG(o.order_amount), 2) AS avg_order_value,
        ROUND(SUM(o.order_amount - p.cost), 2) AS total_profit,
        ROUND((SUM(o.order_amount - p.cost) / SUM(o.order_amount)) * 100.0, 2) AS gross_margin_pct
    FROM products p
    JOIN orders o ON p.product_id = o.product_id
    WHERE o.status = 'Completed'
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY total_revenue DESC
    LIMIT 15;
    """
    df = pd.read_sql(query, conn)
    df = df.sort_values(by='total_revenue', ascending=True) # Ascending for horizontal bar

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['product_name'],
        x=df['total_revenue'],
        orientation='h',
        name='Product Revenue',
        customdata=df[['category', 'order_count', 'avg_order_value', 'gross_margin_pct', 'total_profit']],
        hovertemplate='<b>%{y}</b><br>' +
                      'Category: <b>%{customdata[0]}</b><br>' +
                      'Total Revenue: <b>$%{x:,.2f}</b><br>' +
                      'Total Orders: <b>%{customdata[1]:,}</b><br>' +
                      'Avg Order Value: <b>$%{customdata[2]:,.2f}</b><br>' +
                      'Gross Profit: <b>$%{customdata[4]:,.2f}</b><br>' +
                      'Profit Margin: <b>%{customdata[3]:.1f}%</b><br>' +
                      '<extra></extra>',
        marker=dict(
            color=df['total_revenue'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title='Revenue ($)', tickprefix='$', len=0.8)
        )
    ))

    fig.update_layout(
        title=dict(
            text='<b>Top 15 Products by Revenue (Multi-Column Rich Hover)</b><br><sup>Hover over any bar to inspect Orders, AOV, Gross Profit, and Margin %</sup>',
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Total Revenue ($ USD)',
            showgrid=True,
            gridcolor='#e1e4e8',
            tickprefix='$',
            tickformat=',.0f'
        ),
        yaxis=dict(
            title='Product Name',
            showgrid=False
        ),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='sans-serif'),
        plot_bgcolor='#fafbfc',
        paper_bgcolor='#ffffff',
        height=600,
        margin=dict(l=150, r=50, t=80, b=50)
    )

    fig.write_html('chart2_product_performance.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart2_product_performance.html'))
    print("✔ Chart 2 saved: chart2_product_performance.html")
    return fig


# ==============================================================================
# 🔀 TASK 2: CREATE DROPDOWN FILTER TO TOGGLE VIEWS (NO RELOAD)
# ==============================================================================

def create_chart_3_metric_selector(conn):
    """
    Chart 3: Dropdown Menu to toggle between 3 metrics (Revenue, Profit, Order Count)
    without page reload or re-querying the database.
    """
    print("Generating Chart 3: Metric Selector Dropdown Chart...")

    query = """
    SELECT 
        p.category,
        ROUND(SUM(o.order_amount), 2) AS revenue,
        ROUND(SUM(o.order_amount - p.cost), 2) AS profit,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM products p
    JOIN orders o ON p.product_id = o.product_id
    WHERE o.status = 'Completed'
    GROUP BY p.category
    ORDER BY revenue DESC;
    """
    df = pd.read_sql(query, conn)

    fig = go.Figure()

    # Trace 1: Revenue (Visible initially)
    fig.add_trace(go.Bar(
        x=df['category'],
        y=df['revenue'],
        name='Total Revenue',
        marker=dict(color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Revenue: <b>$%{y:,.2f}</b><extra></extra>',
        visible=True
    ))

    # Trace 2: Profit (Initially hidden)
    fig.add_trace(go.Bar(
        x=df['category'],
        y=df['profit'],
        name='Gross Profit',
        marker=dict(color='#2ca02c'),
        hovertemplate='<b>%{x}</b><br>Gross Profit: <b>$%{y:,.2f}</b><extra></extra>',
        visible=False
    ))

    # Trace 3: Order Count (Initially hidden)
    fig.add_trace(go.Bar(
        x=df['category'],
        y=df['order_count'],
        name='Order Count',
        marker=dict(color='#ff7f0e'),
        hovertemplate='<b>%{x}</b><br>Completed Orders: <b>%{y:,}</b><extra></extra>',
        visible=False
    ))

    # Define Dropdown Updatemenus
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            x=0.0,
            xanchor='left',
            y=1.18,
            yanchor='top',
            bgcolor='#ffffff',
            bordercolor='#cccccc',
            borderwidth=1,
            buttons=[
                dict(
                    label='📊 Total Revenue ($)',
                    method='update',
                    args=[
                        {'visible': [True, False, False]},
                        {
                            'title': '<b>Product Category Performance: Total Revenue</b>',
                            'yaxis': {'title': 'Revenue ($ USD)', 'tickprefix': '$', 'tickformat': ',.0f'}
                        }
                    ]
                ),
                dict(
                    label='💰 Gross Profit ($)',
                    method='update',
                    args=[
                        {'visible': [False, True, False]},
                        {
                            'title': '<b>Product Category Performance: Gross Profit</b>',
                            'yaxis': {'title': 'Gross Profit ($ USD)', 'tickprefix': '$', 'tickformat': ',.0f'}
                        }
                    ]
                ),
                dict(
                    label='📦 Order Volume (Count)',
                    method='update',
                    args=[
                        {'visible': [False, False, True]},
                        {
                            'title': '<b>Product Category Performance: Completed Order Count</b>',
                            'yaxis': {'title': 'Number of Orders', 'tickprefix': '', 'tickformat': ',.0f'}
                        }
                    ]
                )
            ]
        )],
        title=dict(
            text='<b>Product Category Performance (Interactive Metric Selector)</b><br><sup>Select metric from dropdown to dynamically switch view without reloading</sup>',
            font=dict(size=16)
        ),
        xaxis=dict(title='Product Category', showgrid=True, gridcolor='#e1e4e8'),
        yaxis=dict(title='Revenue ($ USD)', tickprefix='$', tickformat=',.0f', showgrid=True, gridcolor='#e1e4e8'),
        plot_bgcolor='#fafbfc',
        paper_bgcolor='#ffffff',
        height=550,
        showlegend=False
    )

    fig.write_html('chart3_metric_selector.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart3_metric_selector.html'))
    print("✔ Chart 3 saved: chart3_metric_selector.html")
    return fig


# ==============================================================================
# 🔍 TASK 3: ENABLE ZOOM, PAN, AND RESET INTERACTIONS
# ==============================================================================

def create_chart_4_interactive(conn):
    """
    Chart 4: Interactive Multi-Dimensional Scatter Plot with native Plotly interactions:
    - Click-and-drag Zoom
    - Shift-click Pan
    - Double-click Reset
    - Box / Lasso multi-point selection
    """
    print("Generating Chart 4: Interactive Scatter with Zoom/Pan/Lasso...")

    query = """
    SELECT 
        o.order_id,
        o.order_date,
        o.order_amount,
        p.product_name,
        p.category,
        p.price AS unit_price,
        ROUND(o.order_amount - p.cost, 2) AS order_profit,
        c.segment AS customer_segment
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Completed'
    LIMIT 1200;
    """
    df = pd.read_sql(query, conn)

    fig = px.scatter(
        df,
        x='order_amount',
        y='order_profit',
        color='category',
        size='order_amount',
        hover_data=['order_id', 'product_name', 'customer_segment', 'order_date'],
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728'],
        title='<b>Multi-Dimensional Order Profitability (Interactive Explorer)</b><br><sup>Supports Click-Drag Zoom, Shift-Drag Pan, Box/Lasso Select, and Double-Click Reset</sup>'
    )

    # Configure native interaction controls
    fig.update_layout(
        dragmode='zoom', # default dragmode: 'zoom', 'pan', 'select', 'lasso'
        hovermode='closest',
        xaxis=dict(
            title='Order Amount ($ USD)',
            tickprefix='$',
            tickformat=',.0f',
            showgrid=True,
            gridcolor='#e1e4e8'
        ),
        yaxis=dict(
            title='Order Gross Profit ($ USD)',
            tickprefix='$',
            tickformat=',.0f',
            showgrid=True,
            gridcolor='#e1e4e8'
        ),
        plot_bgcolor='#fafbfc',
        paper_bgcolor='#ffffff',
        height=620,
        legend=dict(title='Product Category', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        modebar=dict(
            add=['drawline', 'drawopenpath', 'eraseshape'],
            orientation='v',
            bgcolor='rgba(255,255,255,0.8)'
        )
    )

    fig.write_html('chart4_interactive.html')
    fig.write_html(os.path.join(OUTPUT_DIR, 'chart4_interactive.html'))
    print("✔ Chart 4 saved: chart4_interactive.html")
    return fig


def main():
    print("=" * 80)
    print("STARTING ASSIGNMENT: INTERACTIVE PLOTLY CHART DESIGN")
    print("=" * 80)

    db_path = "data_layer.db"
    if not os.path.exists(db_path):
        from database.setup_data_layer import init_data_layer_db
        print(f"Initializing {db_path}...")
        init_data_layer_db(db_path)

    conn = get_db_connection(db_path)

    # Execute all chart creation tasks
    create_chart_1_revenue_trend(conn)
    create_chart_2_product_performance(conn)
    create_chart_3_metric_selector(conn)
    create_chart_4_interactive(conn)

    conn.close()

    print("=" * 80)
    print("ALL 4 PLOTLY CHARTS CREATED AND EXPORTED SUCCESSFULLY AS INTERACTIVE HTML!")
    print(f"Exports available in workspace root and '{OUTPUT_DIR}/'")
    print("=" * 80)

if __name__ == "__main__":
    main()
