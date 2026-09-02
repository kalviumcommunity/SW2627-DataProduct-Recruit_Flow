import io
import pandas as pd
import plotly.express as px
import streamlit as st

from alert_config import ALERT_THRESHOLDS

st.set_page_config(page_title="Real-Time KPI & Workflow Analytics", layout="wide")

# ==========================================
# Task 3 (2.55): Caching Data Loading Functions
# ==========================================
# Use @st.cache_data to prevent redundant recomputation on each interaction.
@st.cache_data
def get_default_data():
    """Generate default analytical dataset cached in memory."""
    dates = pd.date_range(start="2026-01-01", end="2026-08-28", freq="D")
    segments = ["Enterprise", "Mid-Market", "SMB"]
    records = []
    for i, d in enumerate(dates):
        for seg in segments:
            base = 15000 if seg == "Enterprise" else (8000 if seg == "Mid-Market" else 3000)
            rev = base + (i % 15) * 250 + (len(seg) * 50)
            users = int(rev / 45)
            customer_id = f"CUST-{(i % 50) + 100}"
            churn_val = 3.5 if seg == "Enterprise" else (5.8 if seg == "Mid-Market" else 8.5)
            records.append({
                "date": d,
                "segment": seg,
                "revenue": float(rev),
                "users": users,
                "customer_id": customer_id,
                "churn": churn_val,
                "nps": 72
            })
    return pd.DataFrame(records)


@st.cache_data
def load_data(file_bytes, file_name):
    """Load and parse uploaded CSV or JSON datasets, cached by file content."""
    if file_name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif file_name.endswith(".json"):
        return pd.read_json(io.BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file format")


# ==========================================
# Task 1, 2, 5 (2.54): Safe Session State Initialisation & Inline Documentation
# ==========================================

# "selected_segment" - stores the user's segment choice from Step 1
# so it survives reruns when the user interacts with Step 2 widgets.
if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"

# "workflow_step" - tracks which step the user has completed.
# Prevents Step 2 from displaying before Step 1 is confirmed.
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1

# "analysis_result" - caches the computation from Step 2 so
# it does not recompute when unrelated widgets are changed.
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# "filter_date_start" - stores the starting date filter choice
# to maintain date range context across page reloads.
if "filter_date_start" not in st.session_state:
    st.session_state["filter_date_start"] = None

# "computed_revenue" - stores intermediate revenue metrics from analytics workflow.
if "computed_revenue" not in st.session_state:
    st.session_state["computed_revenue"] = 0.0

# "export_ready" - indicates whether the current workflow state is ready for report export.
if "export_ready" not in st.session_state:
    st.session_state["export_ready"] = False


# ==========================================
# Sidebar & Global Controls
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["KPI Dashboard", "Multi-Step Workflow", "Trends & Distribution", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.header("Workflow & Reset Controls")

# Task 4 (2.54): Session State Reset Button
if st.sidebar.button("Reset Workflow"):
    # Clear specific session state keys for workflow progress
    for key in [
        "selected_segment",
        "workflow_step",
        "analysis_result",
        "filter_date_start",
        "computed_revenue",
        "export_ready"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.sidebar.success("Workflow reset to initial state.")
    st.rerun()

st.sidebar.divider()
st.sidebar.header("Dataset & Filters")

# File Uploader
uploaded_file = st.sidebar.file_uploader("Upload CSV/JSON Data", type=["csv", "json"])
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file.getvalue(), uploaded_file.name)
        st.sidebar.success(f"Loaded {uploaded_file.name}")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = get_default_data()
else:
    df = get_default_data()

# Check for expected columns or assign fallback columns for generic handling (Task 5 of 2.55)
has_required_cols = {"date", "segment", "revenue"}.issubset(df.columns)
if not has_required_cols:
    st.sidebar.warning("Uploaded dataset missing standard schema ('date', 'segment', 'revenue'). Operating in generic exploration mode.")

# Filter widgets
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date))
else:
    date_range = None

if "segment" in df.columns:
    all_segments = df["segment"].unique().tolist()
    selected_segments = st.sidebar.multiselect("Segments", options=all_segments, default=all_segments)
else:
    selected_segments = None

if "revenue" in df.columns:
    min_rev_val = float(df["revenue"].min())
    max_rev_val = float(df["revenue"].max())
    rev_range = st.sidebar.slider(
        "Revenue Range",
        min_value=int(min_rev_val),
        max_value=int(max_rev_val),
        value=(int(min_rev_val), int(max_rev_val))
    )
else:
    rev_range = None

# Filter application
filtered_df = df.copy()
if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= date_range[0]) &
        (filtered_df["date"].dt.date <= date_range[1])
    ]
if selected_segments is not None:
    filtered_df = filtered_df[filtered_df["segment"].isin(selected_segments)]
if rev_range is not None:
    filtered_df = filtered_df[
        (filtered_df["revenue"] >= rev_range[0]) &
        (filtered_df["revenue"] <= rev_range[1])
    ]

# Task 4 (2.55): Handle Empty Filtered Results
if len(filtered_df) == 0:
    st.warning("No data matches current filters. Broaden your selection.")
    st.stop()


# ==========================================
# Page 1: Real-Time KPI Dashboard (Task 1 & 2 of 2.55)
# ==========================================
if page == "KPI Dashboard":
    st.title("Real-Time KPI Dashboard")
    st.caption("Live business metrics and interactive visualisations updating reactively with filters.")

    # ==========================================
    # Threshold Monitoring & Visual Alerts (Tasks 1-5)
    # ==========================================
    total_cells = filtered_df.shape[0] * filtered_df.shape[1] if len(filtered_df) > 0 else 0
    churn_val = float(filtered_df["churn"].mean()) if "churn" in filtered_df.columns else (float(filtered_df["churn_rate"].mean()) if "churn_rate" in filtered_df.columns else 0.0)
    aov_val = float(filtered_df["revenue"].mean()) if "revenue" in filtered_df.columns else (float(filtered_df["avg_order_value"].mean()) if "avg_order_value" in filtered_df.columns else 0.0)
    null_val = float(filtered_df["null_percentage"].mean()) if "null_percentage" in filtered_df.columns else ((filtered_df.isnull().sum().sum() / total_cells * 100.0) if total_cells > 0 else 0.0)

    current_metrics = {
        "churn_rate": churn_val,
        "avg_order_value": aov_val,
        "null_percentage": null_val
    }

    for key, config in ALERT_THRESHOLDS.items():
        value = current_metrics.get(key, 0)
        breached = False
        if config["direction"] == "above" and value > config["threshold"]:
            breached = True
        elif config["direction"] == "below" and value < config["threshold"]:
            breached = True

        if breached:
            alert_text = ("ALERT: " + config["metric"]
                          + " is " + str(round(value, 1))
                          + " (threshold: " + str(config["threshold"]) + "). "
                          + config["message"])
            if config["severity"] == "critical":
                st.error(alert_text)
            else:
                st.warning(alert_text)

    # Task 1 (2.55): Five Reactive KPI Metrics from filtered_df
    total_revenue = filtered_df["revenue"].sum() if "revenue" in filtered_df.columns else 0.0
    avg_order = filtered_df["revenue"].mean() if "revenue" in filtered_df.columns else 0.0
    row_count = len(filtered_df)
    unique_customers = filtered_df["customer_id"].nunique() if "customer_id" in filtered_df.columns else len(filtered_df)
    total_cells = filtered_df.shape[0] * filtered_df.shape[1]
    null_pct = (filtered_df.isnull().sum().sum() / total_cells * 100) if total_cells > 0 else 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Avg Order", f"${avg_order:,.0f}")
    with col3:
        st.metric("Records", f"{row_count:,}")
    with col4:
        st.metric("Customers", f"{unique_customers:,}")
    with col5:
        st.metric("Quality", f"{100 - null_pct:.1f}%")

    st.divider()

    # Task 2 (2.55): Include Three Chart Types Wired to Filters
    st.header("Interactive Analytics Visualisations")

    c1, c2 = st.columns(2)
    with c1:
        # Chart 1: Line Chart (Trend over time)
        st.subheader("Revenue Over Time")
        if "date" in filtered_df.columns and "revenue" in filtered_df.columns:
            trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
            st.line_chart(trend.set_index("date"))
        else:
            st.info("Line chart requires 'date' and 'revenue' columns.")

    with c2:
        # Chart 2: Bar Chart (Comparison by Segment)
        st.subheader("Revenue by Segment")
        if "segment" in filtered_df.columns and "revenue" in filtered_df.columns:
            seg = filtered_df.groupby("segment")["revenue"].sum().reset_index()
            st.bar_chart(seg.set_index("segment"))
        else:
            st.info("Bar chart requires 'segment' and 'revenue' columns.")

    # Chart 3: Plotly Histogram (Distribution)
    st.subheader("Order Value Distribution")
    if "revenue" in filtered_df.columns:
        fig = px.histogram(
            filtered_df,
            x="revenue",
            nbins=30,
            title="Revenue Distribution Across Filtered Records",
            labels={"revenue": "Revenue ($)"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Histogram requires numeric 'revenue' column.")


# ==========================================
# Page 2: Multi-Step Workflow (Task 3 of 2.54)
# ==========================================
elif page == "Multi-Step Workflow":
    st.title("Multi-Step Guided Segment Workflow")
    st.caption("Session state persists your selections and step progression across widget interactions.")

    # Step 1: Select Segment
    st.header("Step 1: Select Segment")
    segment_options = ["All", "Enterprise", "Mid-Market", "SMB"]

    # Read default index from session state to keep widget in sync across reruns
    current_segment = st.session_state["selected_segment"]
    default_idx = segment_options.index(current_segment) if current_segment in segment_options else 0

    segment = st.selectbox("Choose a segment", options=segment_options, index=default_idx)

    if st.button("Confirm Segment"):
        st.session_state["selected_segment"] = segment
        st.session_state["workflow_step"] = 2
        st.success(f"Step 1 Confirmed: Selected '{segment}'")

    # Step 2: Show analysis (only if step 1 is complete)
    if st.session_state["workflow_step"] >= 2:
        st.divider()
        st.header("Step 2: Segment Analysis")
        chosen = st.session_state["selected_segment"]
        st.write("Analysing segment: **" + chosen + "**")

        if chosen == "All":
            analysis_df = filtered_df
        else:
            analysis_df = filtered_df[filtered_df["segment"] == chosen] if "segment" in filtered_df.columns else filtered_df

        if len(analysis_df) == 0:
            st.warning("No records match the selected segment under current date/revenue filters.")
        else:
            # Compute and store results in session state
            result = float(analysis_df["revenue"].sum()) if "revenue" in analysis_df.columns else 0.0
            st.session_state["analysis_result"] = result
            st.session_state["computed_revenue"] = result
            st.session_state["export_ready"] = True

            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric("Total Revenue for " + chosen, f"${result:,.0f}")
            with res_col2:
                st.metric("Segment Record Count", f"{len(analysis_df):,}")

            st.subheader("Segment Data Preview")
            st.dataframe(analysis_df.head(10), use_container_width=True)


# ==========================================
# Page 3: Trends & Distribution
# ==========================================
elif page == "Trends & Distribution":
    st.title("Trends & Distribution Analysis")

    st.header("Revenue Trend by Segment")
    if "date" in filtered_df.columns and "segment" in filtered_df.columns and "revenue" in filtered_df.columns:
        pivoted = filtered_df.pivot_table(index="date", columns="segment", values="revenue", aggfunc="sum").fillna(0)
        st.line_chart(pivoted)

    st.divider()
    st.header("User Activity Distribution")
    if "users" in filtered_df.columns:
        fig_users = px.histogram(filtered_df, x="users", nbins=25, title="Active Users Distribution")
        st.plotly_chart(fig_users, use_container_width=True)


# ==========================================
# Page 4: Data Explorer
# ==========================================
elif page == "Data Explorer":
    st.title("Data Explorer & File Inspection")
    st.write(f"Showing {len(filtered_df):,} of {len(df):,} records after filtering.")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Summary Statistics")
    st.dataframe(filtered_df.describe(), use_container_width=True)
