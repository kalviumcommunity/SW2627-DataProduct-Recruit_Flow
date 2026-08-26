from pathlib import Path

import streamlit as st

from components.filters import render_filters
from pages.dashboard import render_dashboard
from pages.drilldown import render_drilldown
from pages.upload import render_upload
from services.analytics import load_data
from utils.session import initialize_session

st.set_page_config(
    page_title="RecruitFlow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session()

st.sidebar.title("RecruitFlow")
st.sidebar.caption("HR hiring intelligence")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Upload Dataset", "Drill-down"],
    label_visibility="collapsed",
)

uploaded_file = st.session_state.get("uploaded_file")
data_path = Path(__file__).parent / "data" / "mock_data.csv"
using_mock_data = uploaded_file is None
data = load_data(uploaded_file if uploaded_file is not None else data_path)

if page == "Dashboard":
    filters = render_filters(data)
    render_dashboard(data, filters, using_mock_data)
elif page == "Upload Dataset":
    render_upload()
else:
    filters = render_filters(data)
    render_drilldown(data, filters)
