from pathlib import Path
from typing import IO

import pandas as pd

STAGES = ["Application", "Screening", "Interview", "Offer", "Joined"]
DISPLAY_STAGES = ["Applied", "Screening", "Interview", "Offer", "Joined"]

MOCK_FUNNEL = {
    "Applied": 4582,
    "Screening": 2891,
    "Interview": 1402,
    "Offer": 412,
    "Joined": 231,
}

MOCK_REASONS = {
    "Technical mismatch": 42,
    "Salary expectations": 25,
    "Candidate withdrawal": 18,
    "Process delay": 10,
    "Other": 5,
}


def load_data(source: str | Path | IO[bytes]) -> pd.DataFrame:
    data = pd.read_csv(source)
    data["application_date"] = pd.to_datetime(data["application_date"])
    return data


def stage_counts(data: pd.DataFrame) -> pd.Series:
    return data[STAGES].sum().astype(int)


def funnel_metrics(counts: dict[str, int]) -> pd.DataFrame:
    rows = []
    previous_count = None
    for stage, count in counts.items():
        conversion = count / counts["Applied"] if counts["Applied"] else 0
        dropoff = (previous_count - count) / previous_count if previous_count else 0
        rows.append({
            "stage": stage,
            "candidates": count,
            "conversion": conversion,
            "dropoff": dropoff,
        })
        previous_count = count
    return pd.DataFrame(rows)


def filtered_data(data: pd.DataFrame, department: str, role: str) -> pd.DataFrame:
    result = data
    if department != "All departments":
        result = result[result["department"] == department]
    if role != "All roles":
        result = result[result["role"] == role]
    return result


def dropoff_reasons(data: pd.DataFrame) -> pd.Series:
    return data.loc[data["dropoff_reason"].notna(), "dropoff_reason"].value_counts()
