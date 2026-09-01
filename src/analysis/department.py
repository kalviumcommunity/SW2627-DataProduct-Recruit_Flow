"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/department.py
Description: Calculate department-wise candidate drop-off rates and delta comparisons.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def calculate_department_dropoff(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes department-wise candidate volume, stage progression,
    worst-stage drop-off rates, and deviation from company benchmark.
    """
    if df.empty:
        return pd.DataFrame()
    
    dept_summary = df.groupby('department').agg(
        total_applied=('candidate_id', 'count'),
        total_joined=('current_stage', lambda x: (x == 'Joined').sum()),
    ).reset_index()
    
    dept_summary['conversion_rate'] = (dept_summary['total_joined'] / dept_summary['total_applied'] * 100).round(2)
    dept_summary['dropoff_rate'] = (100.0 - dept_summary['conversion_rate']).round(2)
    
    overall_avg_dropoff = dept_summary['dropoff_rate'].mean()
    dept_summary['delta_vs_avg'] = (dept_summary['dropoff_rate'] - overall_avg_dropoff).round(2)
    
    return dept_summary.sort_values(by='dropoff_rate', ascending=False)
