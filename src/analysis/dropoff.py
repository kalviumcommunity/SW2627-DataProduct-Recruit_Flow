"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/dropoff.py
Description: Cross-tabulate top drop-off reasons per stage, department, and transition point.
"""

import pandas as pd
from typing import Dict, Any

def cross_tabulate_dropoffs(df_stages: pd.DataFrame, df_candidates: pd.DataFrame = None) -> pd.DataFrame:
    """
    Computes stage-to-stage transition metrics, drop counts, and candidate leak severity.
    """
    if df_stages.empty:
        return pd.DataFrame()
        
    stage_order = ['Application', 'Screening', 'Interview', 'Technical Round', 'HR Round', 'Offer', 'Joined']
    
    stage_counts = df_stages['stage'].value_counts().reindex(stage_order).fillna(0).astype(int)
    
    results = []
    prev_count = None
    for stage, count in stage_counts.items():
        lost = 0 if prev_count is None else max(0, prev_count - count)
        drop_pct = 0.0 if prev_count is None or prev_count == 0 else round((lost / prev_count) * 100, 1)
        
        severity = 'Normal'
        if drop_pct >= 28.0:
            severity = 'Critical Leak'
        elif drop_pct >= 18.0:
            severity = 'Elevated'
            
        results.append({
            'stage': stage,
            'count': int(count),
            'lost': int(lost),
            'dropoff_rate': drop_pct,
            'severity': severity
        })
        prev_count = count
        
    return pd.DataFrame(results)
