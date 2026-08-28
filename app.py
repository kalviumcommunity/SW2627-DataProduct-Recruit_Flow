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

    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            if len(df) == 0:
                st.warning("Uploaded file is empty.")
                st.stop()
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()

        st.success("Loaded: " + uploaded_file.name
                   + " (" + str(len(df)) + " rows, "
                   + str(len(df.columns)) + " columns)")

        st.header("Dataset Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", str(len(df.columns)))
        with col3:
            null_pct = (df.isnull().sum().sum()
                        / (df.shape[0] * df.shape[1]) * 100) if (df.shape[0] * df.shape[1]) > 0 else 0.0
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
        })
        st.dataframe(summary, use_container_width=True)

        st.subheader("Descriptive Statistics")
        st.dataframe(df.describe(), use_container_width=True)

        # Simple demonstration of downstream usage
        st.subheader("Quick Exploration")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select a column to visualise", numeric_cols)
            st.bar_chart(df[selected_col].value_counts().head(20))
        else:
            st.info("No numeric columns available for visualization.")

        with st.expander("About Dataset Processing"):
            st.write("Uploaded datasets are parsed directly in memory. Data preview, column summary, null metrics, and descriptive statistics are automatically generated.")

    else:
        st.info("Upload a CSV or JSON file to begin.")
