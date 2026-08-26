import plotly.express as px
import streamlit as st

from services.analytics import funnel_metrics, stage_counts


def render_funnel(data, using_mock_data: bool = False) -> None:
    counts = data if using_mock_data else stage_counts(data).rename(index={"Application": "Applied"}).to_dict()
    metrics = funnel_metrics(counts)
    figure = px.funnel(metrics, x="candidates", y="stage", color_discrete_sequence=["#0f766e"])
    figure.update_layout(margin=dict(l=0, r=0, t=16, b=0), height=360)
    st.plotly_chart(figure, use_container_width=True)
    table = metrics.copy()
    table["candidates"] = table["candidates"].map(lambda value: f"{value:,}")
    table["conversion"] = table["conversion"].map(lambda value: f"{value:.1%}")
    table["dropoff"] = table["dropoff"].map(lambda value: f"{value:.1%}")
    st.dataframe(
        table.rename(columns={"stage": "Stage", "candidates": "Candidates", "conversion": "Conversion", "dropoff": "Drop-off"}),
        hide_index=True,
        use_container_width=True,
    )
