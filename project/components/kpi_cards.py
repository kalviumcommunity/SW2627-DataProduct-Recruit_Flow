import streamlit as st


def render_kpis(data, using_mock_data: bool = False) -> None:
    if using_mock_data:
        total = data["Applied"]
        offers = data["Offer"]
        joined = data["Joined"]
        dropoff = 70.6
    else:
        total = len(data)
        offers = int(data["Offer"].sum())
        joined = int(data["Joined"].sum())
        dropoff = (1 - joined / total) * 100 if total else 0
    columns = st.columns(4)
    metrics = [
        ("Total Candidates", f"{total:,}"),
        ("Offers", f"{offers:,}"),
        ("Joined", joined),
        ("Overall Drop-off", f"{dropoff:.1f}%"),
    ]
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value)
