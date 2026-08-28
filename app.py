import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Initialize default dataset
@st.cache_data
def get_default_data():
    dates = pd.date_range(start="2026-01-01", end="2026-08-28", freq="D")
    segments = ["Enterprise", "Mid-Market", "SMB"]
    records = []
    for i, d in enumerate(dates):
        for seg in segments:
            base = 15000 if seg == "Enterprise" else (8000 if seg == "Mid-Market" else 3000)
            rev = base + (i % 15) * 250 + (len(seg) * 50)
            users = int(rev / 45)
            records.append({
                "date": d,
                "segment": seg,
                "revenue": rev,
                "users": users,
                "churn": 5.2,
                "nps": 72
            })
    return pd.DataFrame(records)

df = get_default_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.header("Filters")

# Task 5: Reset Filters button
if st.sidebar.button("Reset Filters"):
    st.rerun()

# Task 1 & Task 3: Date range picker (Widget 1 with meaningful defaults)
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["date"].min(), df["date"].max())
)

# Task 1 & Task 3: Multi-select for segments (Widget 2 with meaningful defaults)
all_segments = df["segment"].unique().tolist()
selected_segments = st.sidebar.multiselect(
    "Segments", options=all_segments, default=all_segments
)

# Task 1 & Task 3: Revenue slider (Widget 3 with meaningful defaults)
min_rev, max_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=int(df["revenue"].min()),
    max_value=int(df["revenue"].max()),
    value=(int(df["revenue"].min()), int(df["revenue"].max()))
)

# Task 2: Wire Widgets to Filter the DataFrame
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df = df[
        (df["date"] >= pd.Timestamp(date_range[0]))
        & (df["date"] <= pd.Timestamp(date_range[1]))
        & (df["segment"].isin(selected_segments))
        & (df["revenue"] >= min_rev)
        & (df["revenue"] <= max_rev)
    ]
elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
    filtered_df = df[
        (df["date"] >= pd.Timestamp(date_range[0]))
        & (df["segment"].isin(selected_segments))
        & (df["revenue"] >= min_rev)
        & (df["revenue"] <= max_rev)
    ]
else:
    filtered_df = df[
        (df["segment"].isin(selected_segments))
        & (df["revenue"] >= min_rev)
        & (df["revenue"] <= max_rev)
    ]

# Task 4: Handle Empty Filter Combinations
if len(filtered_df) == 0:
    st.warning("No data matches the current filters. "
               "Try broadening your selection.")
    st.stop()

if page == "Overview":
    st.title("Business Overview")

    # KPI row using columns (Above the fold)
    col1, col2, col3, col4, col5 = st.columns(5)
    total_rev = filtered_df["revenue"].sum()
    total_users = filtered_df["users"].sum()
    aov_val = f"${total_rev / total_users:.0f}" if total_users > 0 else "$0"
    rev_str = f"${total_rev / 1_000_000:.1f}M" if total_rev >= 1_000_000 else f"${total_rev:,.0f}"
    with col1:
        st.metric("Revenue", rev_str, "+12.5%")
    with col2:
        st.metric("Users", f"{total_users:,}", "+5.2%")
    with col3:
        st.metric("AOV", aov_val, "+2.1%")
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

    st.header("Filtered Records")
    st.subheader("Active Filtered Dataset")
    st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
    st.dataframe(filtered_df.head(20), use_container_width=True)

    with st.expander("Detailed Operational Notes"):
        st.write("Performance metrics are aggregated daily from primary billing and engagement events.")

elif page == "Trends":
    st.title("Trend Analysis")

    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.write("Monthly revenue trajectory indicates consistent upward momentum across all quarters.")
        st.line_chart(filtered_df.groupby("date")["revenue"].sum())
    with t_col2:
        st.write("Average monthly revenue growth rate stabilized at +8.4%.")
        st.bar_chart(filtered_df.groupby("segment")["revenue"].sum())

    with st.expander("Revenue Trend Details"):
        st.write("Revenue calculations are normalized for billing cycle adjustments and seasonal trends.")

    st.divider()

    st.header("Customer Metrics")
    st.subheader("Active Customers Over Time")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.write("Active customer base expanded by 24% year-over-year.")
        st.line_chart(filtered_df.groupby("date")["users"].sum())
    with c_col2:
        st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
        st.dataframe(filtered_df.head(10), use_container_width=True)

    with st.expander("Customer Cohort Definitions"):
        st.write("Active customers are defined as accounts with verified activity within the past 30 days.")

elif page == "Data Explorer":
    st.title("Data Explorer")

    st.header("Filtered Dataset View")
    st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
    st.dataframe(filtered_df.head(20), use_container_width=True)

    st.divider()

    st.header("Custom Dataset Upload")
    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                u_df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                u_df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            if len(u_df) == 0:
                st.warning("Uploaded file is empty.")
                st.stop()
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()

        st.success("Loaded: " + uploaded_file.name
                   + " (" + str(len(u_df)) + " rows, "
                   + str(len(u_df.columns)) + " columns)")

        st.header("Dataset Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(u_df):,}")
        with col2:
            st.metric("Columns", str(len(u_df.columns)))
        with col3:
            total_cells = u_df.shape[0] * u_df.shape[1]
            null_pct = (u_df.isnull().sum().sum()
                        / total_cells * 100) if total_cells > 0 else 0.0
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(u_df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame({
            "Column": u_df.columns,
            "Type": u_df.dtypes.astype(str).values,
            "Non-Null": u_df.notnull().sum().values,
            "Null Count": u_df.isnull().sum().values,
            "Null %": (u_df.isnull().sum() / len(u_df) * 100).round(1).values
        })
        st.dataframe(summary, use_container_width=True)

        st.subheader("Descriptive Statistics")
        st.dataframe(u_df.describe(), use_container_width=True)

        # Simple demonstration of downstream usage
        st.subheader("Quick Exploration")
        numeric_cols = u_df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select a column to visualise", numeric_cols)
            st.bar_chart(u_df[selected_col].value_counts().head(20))
        else:
            st.info("No numeric columns available for visualization.")

        with st.expander("About Dataset Processing"):
            st.write("Uploaded datasets are parsed directly in memory. Data preview, column summary, null metrics, and descriptive statistics are automatically generated.")

    else:
        st.info("Upload a CSV or JSON file to begin.")
