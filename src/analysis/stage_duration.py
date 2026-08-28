"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/stage_duration.py
Description: Calculate average and median days spent per recruitment stage.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_stage_latencies(df_stages: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates mean, median, and 90th percentile days spent in each recruitment stage.
    """
    if df_stages.empty or 'entered_at' not in df_stages.columns or 'exited_at' not in df_stages.columns:
        return pd.DataFrame()
        
    df = df_stages.copy()
    df['entered_at'] = pd.to_datetime(df['entered_at'])
    df['exited_at'] = pd.to_datetime(df['exited_at'])
    df['duration_days'] = (df['exited_at'] - df['entered_at']).dt.total_seconds() / 86400.0
    
    latency_summary = df.groupby('stage')['duration_days'].agg(
        avg_days='mean',
        median_days='median',
        p90_days=lambda x: np.percentile(x.dropna(), 90) if len(x.dropna()) > 0 else 0
    ).reset_index()
    
    latency_summary['avg_days'] = latency_summary['avg_days'].round(1)
    latency_summary['median_days'] = latency_summary['median_days'].round(1)
    latency_summary['p90_days'] = latency_summary['p90_days'].round(1)
    
    return latency_summary
