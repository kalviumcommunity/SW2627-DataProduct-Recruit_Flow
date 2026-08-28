import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)

if page == "Overview":
    st.title("Business Overview")

    # KPI row using columns (Above the fold)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Users", "2,500", "+5.2%")
    with col3:
        st.metric("AOV", "$45", "+2.1%")
    with col4:
        st.metric("Churn", "5.2%", "-2.8%", delta_color="inverse")
    with col5:
        st.metric("NPS", "72", "+4")

    # Expander for methodology notes
    with st.expander("About These Metrics"):
        st.write("Revenue is calculated as sum of all order amounts "
                 "for the current month. Churn is the percentage of "
                 "customers who did not return within 30 days.")

    st.divider()

    st.header("Operational Highlights")
    st.subheader("Quarterly Performance Summary")
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.write("Target Achievement: 104.2% of target reached across core segments.")
    with h_col2:
        st.write("Customer Health: Retention rate improved by 2.8% month-over-month.")

    with st.expander("Detailed Operational Notes"):
        st.write("Performance metrics are aggregated daily from primary billing and engagement events.")

elif page == "Trends":
    st.title("Trend Analysis")

    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.write("Monthly revenue trajectory indicates consistent upward momentum across all quarters.")
    with t_col2:
        st.write("Average monthly revenue growth rate stabilized at +8.4%.")

    with st.expander("Revenue Trend Details"):
        st.write("Revenue calculations are normalized for billing cycle adjustments and seasonal trends.")

    st.divider()

    st.header("Customer Metrics")
    st.subheader("Active Customers Over Time")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.write("Active customer base expanded by 24% year-over-year.")
    with c_col2:
        st.write("User engagement frequency rose from 3.2 to 4.5 sessions per week.")

    with st.expander("Customer Cohort Definitions"):
        st.write("Active customers are defined as accounts with verified activity within the past 30 days.")

elif page == "Data Explorer":
    st.title("Data Explorer")

    st.header("Data Filters")
    st.subheader("Query Configuration")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        st.selectbox("Timeframe", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date"])
    with f_col2:
        st.selectbox("Segment", ["All Segments", "Enterprise", "Mid-Market", "SMB"])
    with f_col3:
        st.selectbox("Region", ["Global", "North America", "Europe", "Asia-Pacific"])

    with st.expander("Filter Options & Query Logic"):
        st.write("Filters apply dynamically across all backend metric views and export queries.")

    st.divider()

    st.header("Data Records")
    st.subheader("Metric Summary Table & Export")
    d_col1, d_col2 = st.columns([3, 1])
    sample_df = pd.DataFrame({
        "Date": ["2026-08-01", "2026-08-02", "2026-08-03", "2026-08-04", "2026-08-05"],
        "Metric": ["Revenue", "Users", "AOV", "Churn", "NPS"],
        "Value": ["$5.2M", "2,500", "$45", "5.2%", "72"],
        "Status": ["On Track", "Growing", "Stable", "Optimal", "High"]
    })
    with d_col1:
        st.dataframe(sample_df, use_container_width=True)
    with d_col2:
        st.write("**Export Options**")
        st.download_button(
            label="📥 Export as CSV",
            data=sample_df.to_csv(index=False),
            file_name="analytics_data.csv",
            mime="text/csv"
        )
        st.download_button(
            label="📥 Export as JSON",
            data=sample_df.to_json(orient="records"),
            file_name="analytics_data.json",
            mime="application/json"
        )

    with st.expander("Data Schema & Field Descriptions"):
        st.write("Date: Event record date | Metric: KPI name | Value: Current measurement | Status: Health benchmark.")
