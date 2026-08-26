import streamlit as st

from services.analytics import filtered_data


def render_drilldown(data, filters: dict[str, str]) -> None:
    filtered = filtered_data(data, filters["department"], filters["role"])
    st.title("Candidate Drill-down")
    st.caption("Inspect the candidate-level records behind the dashboard metrics.")
    columns = ["candidate_id", "department", "role", "application_date", "dropoff_reason"]
    st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
