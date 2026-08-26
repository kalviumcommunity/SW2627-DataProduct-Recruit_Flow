import streamlit as st

from services.analytics import funnel_metrics, stage_counts


def render_bottleneck(data, using_mock_data: bool = False) -> None:
    counts = data if using_mock_data else stage_counts(data).rename(index={"Application": "Applied"}).to_dict()
    metrics = funnel_metrics(counts)
    bottleneck = metrics.iloc[1:].loc[metrics.iloc[1:]["dropoff"].idxmax()]
    previous_stage = metrics.iloc[metrics.index.get_loc(bottleneck.name) - 1]["stage"]
    st.warning(
        f"⚠ Biggest Bottleneck: **{previous_stage} → {bottleneck['stage']}** "
        f"({bottleneck['dropoff']:.1%} drop-off)"
    )
