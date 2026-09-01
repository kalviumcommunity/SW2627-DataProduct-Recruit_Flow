"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/role.py
Description: Drill down into specific roles within departments (e.g. IT -> Backend Developer vs QA Engineer).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calculate_role_breakdown(df: pd.DataFrame, department: str = None) -> pd.DataFrame:
    """
    Computes role-specific volume, drop-off rates, and bottleneck stages.
    """
    if df.empty:
        return pd.DataFrame()
        
    filtered = df if not department or department == 'All' else df[df['department'] == department]
    
    role_summary = filtered.groupby(['department', 'job_role']).agg(
        applied=('candidate_id', 'count'),
        joined=('current_stage', lambda x: (x == 'Joined').sum()),
    ).reset_index()
    
    role_summary['conversion_rate'] = (role_summary['joined'] / role_summary['applied'] * 100).round(1)
    role_summary['dropoff_rate'] = (100.0 - role_summary['conversion_rate']).round(1)
    
    return role_summary.sort_values(by=['department', 'dropoff_rate'], ascending=[True, False])
