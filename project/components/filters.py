import streamlit as st


def render_filters(data) -> dict[str, str]:
    departments = ["All departments", *sorted(data["department"].dropna().unique())]
    roles = ["All roles", *sorted(data["role"].dropna().unique())]
    first, second = st.columns(2)
    department = first.selectbox("Department", departments)
    role = second.selectbox("Role", roles)
    return {"department": department, "role": role}
