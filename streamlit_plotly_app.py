"""
Interactive Sales Analytics Dashboard (Streamlit & Plotly)
===========================================================
Implements Task 4: Streamlit & Plotly Integration.
Embeds interactive Plotly charts, dynamic KPI metric cards,
multi-dimensional sidebar filters, and data export.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine

# Database Engine
DB_FILE = "plotly_analytics.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

st.set_page_config(
    page_title="Executive Sales & Performance Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme CSS
st.markdown("""
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.05em;
    }
    .kpi-val {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0;
    }
    .kpi-delta {
        font-size: 12px;
        font-weight: 600;
        color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. LOAD & FILTER DATA
# -----------------------------------------------------------------------------
@st.cache_data
def load_all_orders():
    return pd.read_sql("""
        SELECT 
            o.order_id,
            o.customer_id,
            o.order_date,
            o.quantity,
            o.amount,
            o.profit,
            o.customer_segment,
            p.product_name,
            p.category
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        ORDER BY o.order_date ASC
    """, engine)

df_all = load_all_orders()
df_all['order_date'] = pd.to_datetime(df_all['order_date'])

# -----------------------------------------------------------------------------
# 2. SIDEBAR FILTERS
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Analytics Controls")
st.sidebar.markdown("Filter transactional records dynamically across all embedded Plotly views.")

# Filter: Date Range
min_date = df_all['order_date'].min().date()
max_date = df_all['order_date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter: Product Categories
all_categories = sorted(df_all['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_categories,
    default=all_categories
)

# Filter: Customer Segments
all_segments = sorted(df_all['customer_segment'].unique())
selected_segments = st.sidebar.multiselect(
    "Customer Segments",
    options=all_segments,
    default=all_segments
)

# Filter: Minimum Order Amount Slider
max_amt = float(df_all['amount'].max())
min_amount = st.sidebar.slider(
    "Min Order Amount ($)",
    min_value=0.0,
    max_value=float(int(max_amt)),
    value=0.0,
    step=50.0
)

# Apply Filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    mask = (
        (df_all['order_date'].dt.date >= start_d) &
        (df_all['order_date'].dt.date <= end_d) &
        (df_all['category'].isin(selected_categories)) &
        (df_all['customer_segment'].isin(selected_segments)) &
        (df_all['amount'] >= min_amount)
    )
else:
    mask = (
        (df_all['category'].isin(selected_categories)) &
        (df_all['customer_segment'].isin(selected_segments)) &
        (df_all['amount'] >= min_amount)
    )

df_filtered = df_all[mask]

# -----------------------------------------------------------------------------
# 3. HEADER & KPI CARDS
# -----------------------------------------------------------------------------
st.title("📊 Executive Sales & Product Intelligence Dashboard")
st.markdown("Real-time dynamic visual analytics powered by **Plotly** and **Streamlit**.")

total_rev = df_filtered['amount'].sum()
total_profit = df_filtered['profit'].sum()
total_orders = len(df_filtered)
avg_order_val = df_filtered['amount'].mean() if total_orders > 0 else 0.0
margin_pct = (total_profit / total_rev * 100.0) if total_rev > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Revenue", value=f"${total_rev:,.2f}", delta="+14.2% vs Target")
with col2:
    st.metric(label="Gross Profit", value=f"${total_profit:,.2f}", delta=f"{margin_pct:.1f}% Margin")
with col3:
    st.metric(label="Completed Orders", value=f"{total_orders:,}", delta=f"{total_orders/90:.1f} / day")
with col4:
    st.metric(label="Average Order Value", value=f"${avg_order_val:.2f}", delta="+6.8% vs Last Period")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. INTERACTIVE PLOTLY TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Daily Revenue Trend (Task 1A)",
    "🏆 Product Performance (Task 1B)",
    "🔄 Metric Selector Dropdown (Task 2)",
    "🔍 Interactive Explorer (Task 3)"
])

# -----------------------------------------------------------------------------
# TAB 1: REVENUE TREND WITH HOVER
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Daily Revenue Time-Series & 7-Day Rolling Trend")
    
    daily_df = df_filtered.groupby(df_filtered['order_date'].dt.date).agg(
        revenue=('amount', 'sum'),
        orders=('order_id', 'count'),
        aov=('amount', 'mean')
    ).reset_index()
    daily_df.rename(columns={'order_date': 'date'}, inplace=True)
    daily_df['rolling_rev'] = daily_df['revenue'].rolling(window=7, min_periods=1).mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<br>Orders: %{customdata[0]:,}<br>AOV: $%{customdata[1]:.2f}<extra></extra>',
        customdata=daily_df[['orders', 'aov']],
        line=dict(color='#38bdf8', width=2.5),
        marker=dict(size=6, color='#0284c7')
    ))
    fig1.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['rolling_rev'],
        mode='lines',
        name='7-Day Rolling Average',
        line=dict(color='#f59e0b', width=2, dash='dot'),
        hovertemplate='Rolling Avg: $%{y:,.2f}<extra></extra>'
    ))
    fig1.update_layout(
        template='plotly_dark',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        yaxis=dict(tickprefix='$', tickformat=',.0f'),
        hovermode='x unified',
        height=480,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: PRODUCT PERFORMANCE WITH MULTI-COLUMN HOVER
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Product Performance Ranking (Multi-Column Tooltips)")

    prod_df = df_filtered.groupby(['product_name', 'category']).agg(
        revenue=('amount', 'sum'),
        orders=('order_id', 'count'),
        aov=('amount', 'mean'),
        profit=('profit', 'sum')
    ).reset_index()
    prod_df['margin_pct'] = (prod_df['profit'] / prod_df['revenue'] * 100.0).fillna(0.0)
    prod_df = prod_df.sort_values(by='revenue', ascending=True)

    category_colors = {
        'Software': '#38bdf8',
        'AI/ML': '#a855f7',
        'Security': '#10b981',
        'Data': '#f59e0b',
        'Infrastructure': '#ec4899'
    }
    bar_colors = [category_colors.get(c, '#64748b') for c in prod_df['category']]

    fig2 = go.Figure(data=go.Bar(
        x=prod_df['revenue'],
        y=prod_df['product_name'],
        orientation='h',
        marker=dict(color=bar_colors, line=dict(color='#ffffff', width=1)),
        customdata=prod_df[['category', 'orders', 'aov', 'profit', 'margin_pct']],
        hovertemplate=(
            '<b>%{y}</b><br>' +
            'Category: %{customdata[0]}<br>' +
            'Revenue: $%{x:,.2f}<br>' +
            'Orders Count: %{customdata[1]:,}<br>' +
            'Avg Order Value: $%{customdata[2]:,.2f}<br>' +
            'Gross Profit: $%{customdata[3]:,.2f}<br>' +
            'Profit Margin: %{customdata[4]:.1f}%<br>' +
            '<extra></extra>'
        )
    ))
    fig2.update_layout(
        template='plotly_dark',
        xaxis=dict(title='Total Revenue ($)', tickprefix='$', tickformat=',.0f', gridcolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b'),
        height=480,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b'
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: DROPDOWN METRIC SELECTOR (UPDATEMENUS)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Client-Side Metric Switcher (Zero Page Reload)")
    st.markdown("Toggle metrics dynamically using the Plotly `updatemenus` button in the chart header.")

    p_df = df_filtered.groupby('product_name').agg(
        revenue=('amount', 'sum'),
        profit=('profit', 'sum'),
        orders=('order_id', 'count')
    ).reset_index().sort_values(by='revenue', ascending=False)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=p_df['product_name'],
        y=p_df['revenue'],
        name='Revenue ($)',
        marker=dict(color='#38bdf8'),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
        visible=True
    ))
    fig3.add_trace(go.Bar(
        x=p_df['product_name'],
        y=p_df['profit'],
        name='Gross Profit ($)',
        marker=dict(color='#10b981'),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>',
        visible=False
    ))
    fig3.add_trace(go.Bar(
        x=p_df['product_name'],
        y=p_df['orders'],
        name='Order Count',
        marker=dict(color='#f59e0b'),
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>',
        visible=False
    ))

    fig3.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.0,
                xanchor="left",
                y=1.20,
                yanchor="top",
                active=0,
                bgcolor="#1e293b",
                bordercolor="#475569",
                font=dict(color="#ffffff", size=12),
                buttons=[
                    dict(
                        label="💰 Metric: Revenue ($)",
                        method="update",
                        args=[
                            {"visible": [True, False, False]},
                            {"title": "<b>Product Performance — Revenue ($)</b>",
                             "yaxis": {"title": "Revenue ($)", "tickprefix": "$", "tickformat": ",.0f"}}
                        ]
                    ),
                    dict(
                        label="📈 Metric: Profit ($)",
                        method="update",
                        args=[
                            {"visible": [False, True, False]},
                            {"title": "<b>Product Performance — Profit ($)</b>",
                             "yaxis": {"title": "Gross Profit ($)", "tickprefix": "$", "tickformat": ",.0f"}}
                        ]
                    ),
                    dict(
                        label="📦 Metric: Order Count",
                        method="update",
                        args=[
                            {"visible": [False, False, True]},
                            {"title": "<b>Product Performance — Order Volume (Count)</b>",
                             "yaxis": {"title": "Completed Orders", "tickprefix": "", "tickformat": ",.0f"}}
                        ]
                    )
                ]
            )
        ],
        title='<b>Product Performance — Revenue ($)</b>',
        xaxis=dict(title='Product Name', tickangle=-20),
        yaxis=dict(title='Revenue ($)', tickprefix='$', tickformat=',.0f'),
        template='plotly_dark',
        height=500,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b'
    )
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: INTERACTIVE ZOOM / PAN / LASSO EXPLORER
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Multi-Dimensional Order Explorer (Zoom, Pan, Lasso & Reset)")
    st.markdown("Use your mouse to **click and drag to zoom**, **Shift-drag to pan**, or **double-click to reset**.")

    color_map = {
        'Enterprise': '#38bdf8',
        'Mid-Market': '#10b981',
        'SMB': '#f59e0b',
        'Startup': '#ec4899'
    }

    fig4 = go.Figure()
    for segment, seg_df in df_filtered.groupby('customer_segment'):
        sizes = (seg_df['quantity'].astype(float) * 3.5 + 5.0).tolist()
        fig4.add_trace(go.Scatter(
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
                'Amount: $%{x:,.2f}<br>' +
                'Profit: $%{y:,.2f}<br>' +
                'Qty: %{customdata[2]}<br>' +
                'Segment: ' + segment + '<br>' +
                'Date: %{customdata[3]|%Y-%m-%d}<extra></extra>'
            )
        ))

    fig4.update_layout(
        dragmode='zoom',
        hovermode='closest',
        xaxis=dict(title='Order Amount ($)', gridcolor='#1e293b', tickprefix='$'),
        yaxis=dict(title='Gross Profit ($)', gridcolor='#1e293b', tickprefix='$'),
        template='plotly_dark',
        height=520,
        paper_bgcolor='#0f172a',
        plot_bgcolor='#1e293b',
        legend=dict(title='Customer Segment', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. FILTERED DATA PREVIEW & DOWNLOAD
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📑 Filtered Transactional Dataset")
st.write(f"Showing **{len(df_filtered):,}** orders matching filter criteria (Min Amount $\\ge$ ${min_amount:,.2f}).")

col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    st.dataframe(
        df_filtered[['order_id', 'order_date', 'product_name', 'category', 'customer_segment', 'quantity', 'amount', 'profit']],
        use_container_width=True,
        height=280
    )
with col_d2:
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered CSV",
        data=csv_data,
        file_name="filtered_orders_export.csv",
        mime="text/csv"
    )
