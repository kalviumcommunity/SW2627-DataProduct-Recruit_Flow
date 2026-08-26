import streamlit as st


def initialize_session() -> None:
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
