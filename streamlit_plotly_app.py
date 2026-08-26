"""
Interactive Sales & Revenue Dashboard (Streamlit + Plotly Integration)
File: streamlit_plotly_app.py

Implements Task 4: Embeds interactive Plotly charts with reactive Streamlit widgets:
- Sidebar filters (Date range, Order Amount slider, Category selector, Customer Segment)
- Executive KPI summary metrics
- Multi-tab Plotly visualizations:
    Tab 1: Daily Revenue Trend (with unified hover and rolling avg)
    Tab 2: Product Performance (with multi-column rich hover)
    Tab 3: Dynamic Metric Dropdown Switcher (Revenue vs Profit vs Orders)
    Tab 4: Scatter Plot Explorer (Zoom/Pan/Lasso select)
- Real-time filtered tabular data preview with CSV export
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Executive Sales Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 8px;
        padding-bottom: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 2. Database Loader
@st.cache_data
def load_data(db_path="data_layer.db"):
    if not os.path.exists(db_path):
        from database.setup_data_layer import init_data_layer_db
        init_data_layer_db(db_path)
    
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        o.order_id,
        o.order_date,
        o.order_amount,
        o.status,
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        p.cost,
        ROUND(o.order_amount - p.cost, 2) AS profit,
        c.customer_id,
        c.customer_name,
        c.segment AS customer_segment,
        c.country
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Completed';
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df_raw = load_data()

# 3. Sidebar Filters
st.sidebar.title("🎛️ Dashboard Filters")

# Date range filter
min_date = df_raw['order_date'].min().date()
max_date = df_raw['order_date'].max().date()
selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Product category filter
all_categories = sorted(df_raw['category'].unique())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_categories,
    default=all_categories
)

# Customer segment filter
all_segments = sorted(df_raw['customer_segment'].unique())
selected_segments = st.sidebar.multiselect(
    "Customer Segments",
    options=all_segments,
    default=all_segments
)

# Min order amount slider
max_order_amt = int(df_raw['order_amount'].max())
min_amount = st.sidebar.slider(
    "Min Order Amount ($)",
    min_value=0,
    max_value=max_order_amt,
    value=0,
    step=50
)

# Apply reactive filters
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_d, end_d = selected_dates
    mask = (
        (df_raw['order_date'].dt.date >= start_d) &
        (df_raw['order_date'].dt.date <= end_d) &
        (df_raw['category'].isin(selected_categories)) &
        (df_raw['customer_segment'].isin(selected_segments)) &
        (df_raw['order_amount'] >= min_amount)
    )
    df = df_raw[mask]
else:
    df = df_raw

# 4. Header & Executive KPIs
st.title("📈 Executive Sales & Revenue Intelligence")
st.markdown("Interactive analytical dashboard powered by **Plotly** and **Streamlit**.")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_revenue = df['order_amount'].sum()
total_profit = df['profit'].sum()
total_orders = len(df)
avg_aov = df['order_amount'].mean() if total_orders > 0 else 0
margin_pct = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

with kpi1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}", delta=f"{len(df)} orders")
with kpi2:
    st.metric("Gross Profit", f"${total_profit:,.2f}", delta=f"{margin_pct:.1f}% Margin")
with kpi3:
    st.metric("Total Completed Orders", f"{total_orders:,}")
with kpi4:
    st.metric("Avg Order Value (AOV)", f"${avg_aov:,.2f}")

st.markdown("---")

# 5. Interactive Visualization Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Revenue Trend (Hover)",
    "🏆 Product Performance",
    "🔀 Metric Switcher (Dropdown)",
    "🔍 Order Explorer (Zoom/Pan)",
    "📋 Filtered Data Table"
])

# ------------------------------------------------------------------------------
# TAB 1: DAILY REVENUE TREND
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Daily Revenue Trend with Unified Hover Tooltips")
    
    daily_df = df.groupby(df['order_date'].dt.date).agg(
        revenue=('order_amount', 'sum'),
        order_count=('order_id', 'count'),
        avg_aov=('order_amount', 'mean')
    ).reset_index()
    daily_df.rename(columns={'order_date': 'date'}, inplace=True)
    daily_df['rolling_7d'] = daily_df['revenue'].rolling(window=7, min_periods=1).mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        customdata=daily_df[['order_count', 'avg_aov']],
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                      'Revenue: <b>$%{y:,.2f}</b><br>' +
                      'Orders: <b>%{customdata[0]:,}</b><br>' +
                      'AOV: <b>$%{customdata[1]:,.2f}</b><extra></extra>',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=6)
    ))
    fig1.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['rolling_7d'],
        mode='lines',
        name='7-Day Moving Avg',
        line=dict(color='#ff7f0e', width=2, dash='dot'),
        hovertemplate='7-Day Avg: <b>$%{y:,.2f}</b><extra></extra>'
    ))
    fig1.update_layout(
        xaxis_title='Date',
        yaxis_title='Revenue ($ USD)',
        yaxis=dict(tickprefix='$', tickformat=',.0f'),
        hovermode='x unified',
        height=500,
        legend=dict(orientation='h', y=1.1, x=1, xanchor='right')
    )
    st.plotly_chart(fig1, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: PRODUCT PERFORMANCE
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Top Products by Revenue (Multi-Column Rich Hover)")
    
    prod_df = df.groupby(['product_name', 'category']).agg(
        revenue=('order_amount', 'sum'),
        orders=('order_id', 'count'),
        aov=('order_amount', 'mean'),
        profit=('profit', 'sum')
    ).reset_index()
    prod_df['margin_pct'] = (prod_df['profit'] / prod_df['revenue']) * 100.0
    prod_df = prod_df.sort_values(by='revenue', ascending=True).tail(15)

    fig2 = go.Figure(data=go.Bar(
        y=prod_df['product_name'],
        x=prod_df['revenue'],
        orientation='h',
        customdata=prod_df[['category', 'orders', 'aov', 'margin_pct', 'profit']],
        hovertemplate='<b>%{y}</b><br>' +
                      'Category: <b>%{customdata[0]}</b><br>' +
                      'Total Revenue: <b>$%{x:,.2f}</b><br>' +
                      'Orders: <b>%{customdata[1]:,}</b><br>' +
                      'AOV: <b>$%{customdata[2]:,.2f}</b><br>' +
                      'Gross Profit: <b>$%{customdata[4]:,.2f}</b><br>' +
                      'Margin: <b>%{customdata[3]:.1f}%</b><extra></extra>',
        marker=dict(
            color=prod_df['revenue'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title='Revenue ($)', tickprefix='$')
        )
    ))
    fig2.update_layout(
        xaxis_title='Total Revenue ($ USD)',
        yaxis_title='Product Name',
        yaxis=dict(tickfont=dict(size=10)),
        height=550
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: METRIC SELECTOR DROPDOWN
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Category Performance: Dynamic Dropdown Switcher")
    
    cat_df = df.groupby('category').agg(
        revenue=('order_amount', 'sum'),
        profit=('profit', 'sum'),
        order_count=('order_id', 'count')
    ).reset_index()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=cat_df['category'], y=cat_df['revenue'], name='Revenue', marker=dict(color='#1f77b4'), visible=True))
    fig3.add_trace(go.Bar(x=cat_df['category'], y=cat_df['profit'], name='Profit', marker=dict(color='#2ca02c'), visible=False))
    fig3.add_trace(go.Bar(x=cat_df['category'], y=cat_df['order_count'], name='Orders', marker=dict(color='#ff7f0e'), visible=False))

    fig3.update_layout(
        updatemenus=[dict(
            active=0,
            x=0.0,
            y=1.18,
            yanchor='top',
            buttons=[
                dict(label='📊 Revenue ($)', method='update', args=[{'visible': [True, False, False]}, {'title': 'Category Total Revenue', 'yaxis': {'title': 'Revenue ($)', 'tickprefix': '$'}}]),
                dict(label='💰 Gross Profit ($)', method='update', args=[{'visible': [False, True, False]}, {'title': 'Category Gross Profit', 'yaxis': {'title': 'Profit ($)', 'tickprefix': '$'}}]),
                dict(label='📦 Order Count', method='update', args=[{'visible': [False, False, True]}, {'title': 'Category Order Volume', 'yaxis': {'title': 'Order Count', 'tickprefix': ''}}])
            ]
        )],
        xaxis_title='Product Category',
        yaxis_title='Revenue ($ USD)',
        height=500
    )
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: INTERACTIVE ORDER EXPLORER
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Order Profitability Explorer (Zoom / Pan / Lasso / Box Select)")
    st.info("💡 **Interaction Tip:** Click & drag on the chart to Zoom. Shift+drag to Pan. Double-click to Reset view. Use the top toolbar to activate Box or Lasso selection.")
    
    fig4 = px.scatter(
        df.head(1000),
        x='order_amount',
        y='profit',
        color='category',
        size='order_amount',
        hover_data=['order_id', 'product_name', 'customer_segment', 'order_date'],
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728'],
        title='Order Amount vs. Gross Profit Correlation'
    )
    fig4.update_layout(
        dragmode='zoom',
        xaxis=dict(title='Order Amount ($ USD)', tickprefix='$', tickformat=',.0f'),
        yaxis=dict(title='Order Profit ($ USD)', tickprefix='$', tickformat=',.0f'),
        height=550
    )
    st.plotly_chart(fig4, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 5: FILTERED DATA PREVIEW
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("Underlying Filtered Transaction Records")
    st.write(f"Showing **{len(df):,}** completed orders matching active filters.")
    display_cols = ['order_id', 'order_date', 'customer_name', 'customer_segment', 'product_name', 'category', 'order_amount', 'profit']
    st.dataframe(df[display_cols].head(500), use_container_width=True)
    
    csv_bytes = df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset as CSV",
        data=csv_bytes,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )
