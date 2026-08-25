import os
import json
import pytest
import pandas as pd
from src.analysis.intelligence import generate_hr_intelligence

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "hr_intelligence_recommendations.csv")
JSON_PATH = os.path.join(BASE_DIR, "data", "processed", "hr_intelligence_recommendations.json")

def test_generate_hr_intelligence_generates_outputs():
    generate_hr_intelligence()
    assert os.path.exists(CSV_PATH), f"{CSV_PATH} should exist"
    assert os.path.exists(JSON_PATH), f"{JSON_PATH} should exist"

def test_hr_intelligence_recommendations_structure():
    generate_hr_intelligence()
    df = pd.read_csv(CSV_PATH)
    assert not df.empty
    expected_cols = [
        "id", "priority", "category", "target_stage", 
        "target_department", "issue", "recommended_action", "expected_impact"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column {col} should be in recommendations CSV"

def test_hr_intelligence_anomalies_and_recs_json():
    generate_hr_intelligence()
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
        
    assert "anomalies_detected" in data
    assert "recommendations" in data
    assert "recommendations_count" in data
    assert len(data["anomalies_detected"]) > 0
    assert len(data["recommendations"]) > 0
    
    # Check that high priority recommendations exist
    priorities = [r["priority"] for r in data["recommendations"]]
    assert "HIGH" in priorities
    
    # Check that anomalies detected contain percentages above benchmark
    for a in data["anomalies_detected"]:
        assert "percentage_above_benchmark" in a
        assert a["percentage_above_benchmark"] >= 15.0 or a["type"] == "DELAYED_DROPOFF_INEFFICIENCY"
