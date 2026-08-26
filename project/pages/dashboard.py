import streamlit as st

from components.bottleneck import render_bottleneck
from components.funnel import render_funnel
from components.kpi_cards import render_kpis
from components.reason_chart import render_reason_chart
from services.analytics import MOCK_FUNNEL, MOCK_REASONS, filtered_data


def render_dashboard(data, filters: dict[str, str], using_mock_data: bool = False) -> None:
    filtered = filtered_data(data, filters["department"], filters["role"])
    st.title("Recruitment Dashboard")
    st.caption("A clear view of candidate movement from application to joining.")
    dashboard_data = MOCK_FUNNEL if using_mock_data else filtered
    render_kpis(dashboard_data, using_mock_data)
    render_bottleneck(dashboard_data, using_mock_data)
    left, right = st.columns(2)
    with left:
        st.subheader("Hiring funnel")
        render_funnel(dashboard_data, using_mock_data)
    with right:
        st.subheader("Drop-off reasons")
        render_reason_chart(dashboard_data, using_mock_data)
