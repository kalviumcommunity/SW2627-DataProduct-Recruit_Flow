import os
import json
import pytest
import pandas as pd
from src.analysis.stage_duration import calculate_stage_durations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "stage_duration_summary.csv")
JSON_PATH = os.path.join(BASE_DIR, "data", "processed", "stage_duration_summary.json")

def test_calculate_stage_durations_generates_outputs():
    # Execute calculation function
    calculate_stage_durations()
    
    assert os.path.exists(CSV_PATH), f"{CSV_PATH} should exist after calculation"
    assert os.path.exists(JSON_PATH), f"{JSON_PATH} should exist after calculation"

def test_stage_duration_summary_structure():
    calculate_stage_durations()
    
    df = pd.read_csv(CSV_PATH)
    assert not df.empty
    expected_cols = [
        "stage_order", "stage", "candidates_count", 
        "avg_duration_days", "median_duration_days", 
        "min_duration_days", "max_duration_days", 
        "is_bottleneck", "bottleneck_severity"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column {col} should be in stage duration summary CSV"

def test_stage_duration_json_payload():
    calculate_stage_durations()
    
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
        
    assert "stage_metrics" in data
    assert "department_velocity" in data
    assert "outcome_velocity" in data
    assert "bottleneck_insights" in data
    
    # Validate stage metrics
    stage_metrics = data["stage_metrics"]
    assert len(stage_metrics) == 5
    stage_names = [s["stage"] for s in stage_metrics]
    assert stage_names == ["Application", "Screening", "Interview", "Offer", "Joined"]
    
    # Validate outcome velocity
    outcome_vel = data["outcome_velocity"]
    assert "overall_time_to_hire" in outcome_vel
    assert "overall_time_to_drop" in outcome_vel
    assert outcome_vel["overall_time_to_hire"]["avg_days"] > 0
    assert outcome_vel["overall_time_to_drop"]["avg_days"] > 0
