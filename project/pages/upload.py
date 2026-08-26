import streamlit as st


def render_upload() -> None:
    st.title("Upload Dataset")
    st.write("Upload a CSV with the recruitment funnel fields to explore your own data.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"Loaded {uploaded_file.name}")
        st.dataframe(uploaded_file, use_container_width=True)
    else:
        st.info("The dashboard is currently using the included mock dataset.")
