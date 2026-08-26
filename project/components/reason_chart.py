import pandas as pd
import plotly.express as px
import streamlit as st

from services.analytics import MOCK_REASONS, dropoff_reasons


def render_reason_chart(data, using_mock_data: bool = False) -> None:
    reasons = pd.DataFrame(list((MOCK_REASONS if using_mock_data else dropoff_reasons(data).to_dict()).items()), columns=["reason", "percent"])
    figure = px.bar(reasons, x="percent", y="reason", orientation="h", text="percent", color_discrete_sequence=["#e07a5f"])
    figure.update_traces(texttemplate="%{text}%", textposition="outside")
    figure.update_layout(margin=dict(l=0, r=0, t=16, b=0), height=320, yaxis_title=None, xaxis_title="Share of drop-offs (%)")
    st.plotly_chart(figure, use_container_width=True)
