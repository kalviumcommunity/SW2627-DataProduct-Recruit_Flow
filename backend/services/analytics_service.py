import os
import json
from typing import Dict, Any, List

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

def get_funnel_summary() -> List[Dict[str, Any]]:
    """Reads processed recruitment funnel summary JSON."""
    json_path = os.path.join(PROCESSED_DIR, "recruitment_funnel_summary.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return []

def get_candidate_features() -> List[Dict[str, Any]]:
    """Reads processed candidate features from JSON or CSV."""
    journeys_path = os.path.join(PROCESSED_DIR, "candidate_journeys.json")
    if os.path.exists(journeys_path):
        with open(journeys_path, "r") as f:
            return json.load(f)
    return []

def get_department_summary() -> List[Dict[str, Any]]:
    """Reads processed department analysis summary JSON."""
    json_path = os.path.join(PROCESSED_DIR, "department_analysis_summary.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return []

def get_role_summary() -> List[Dict[str, Any]]:
    """Reads processed role analysis summary JSON."""
    json_path = os.path.join(PROCESSED_DIR, "role_analysis_summary.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return []
