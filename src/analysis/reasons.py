"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/reasons.py
Description: Aggregate rejection and drop-off feedback reasons across stages and departments.
"""

import pandas as pd
from typing import Dict, List, Any

def aggregate_reasons(df_interviews: pd.DataFrame, stage: str = None, department: str = None) -> pd.DataFrame:
    """
    Aggregates structured rejection reasons and percentages for a given stage/department.
    """
    if df_interviews.empty:
        return pd.DataFrame()
        
    filtered = df_interviews.copy()
    if stage and stage != 'All':
        filtered = filtered[filtered['interview_stage'] == stage]
    if department and department != 'All' and 'department' in filtered.columns:
        filtered = filtered[filtered['department'] == department]
        
    reasons_count = filtered['rejection_reason'].value_counts().reset_index()
    reasons_count.columns = ['reason', 'count']
    total_rejections = reasons_count['count'].sum()
    
    if total_rejections > 0:
        reasons_count['percentage'] = (reasons_count['count'] / total_rejections * 100).round(1)
    else:
        reasons_count['percentage'] = 0.0
        
    return reasons_count
