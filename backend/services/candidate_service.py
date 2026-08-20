import os
import json
from typing import Dict, Any, List, Optional

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

def get_candidate_journey(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves single candidate journey by candidate_id."""
    journeys_path = os.path.join(PROCESSED_DIR, "candidate_journeys.json")
    if os.path.exists(journeys_path):
        with open(journeys_path, "r") as f:
            journeys = json.load(f)
            for c in journeys:
                if c.get("candidate_id") == candidate_id:
                    return c
    return None
