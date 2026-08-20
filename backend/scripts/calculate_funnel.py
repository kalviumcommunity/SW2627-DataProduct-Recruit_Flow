import os
import glob
import json
import pandas as pd
import numpy as np

SRC_FEATURES = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_features\candidate_features.csv"
SRC_JOURNEYS = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_integrated\candidate_journeys.json"
DEST_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_analytics"

STAGE_ORDER = ["Application", "Screening", "Interview", "Offer", "Joined"]

def calculate_funnel():
    print("="*60)
    print(" STARTING RECRUITMENT FUNNEL AGGREGATION & METRICS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    df = pd.read_csv(SRC_FEATURES)
    with open(SRC_JOURNEYS, "r") as f:
        journeys = json.load(f)
        
    total_candidates = len(df)
    
    # 1. Count candidates per stage
    # A candidate reached stage i if furthest_stage_index >= i
    stage_counts = {}
    for idx, stage in enumerate(STAGE_ORDER):
        count = len(df[df['furthest_stage_index'] >= idx])
        stage_counts[stage] = count
        
    # 2. Compute conversion & drop-off metrics per stage transition
    funnel_rows = []
    
    for idx, stage in enumerate(STAGE_ORDER):
        current_count = stage_counts[stage]
        next_stage = STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else None
        next_count = stage_counts[next_stage] if next_stage else None
        
        if next_count is not None and current_count > 0:
            conversion_pct = round((next_count / current_count) * 100.0, 1)
            dropoff_pct = round(100.0 - conversion_pct, 1)
            dropoff_count = current_count - next_count
        else:
            conversion_pct = None
            dropoff_pct = None
            dropoff_count = 0
            
        # Overall conversion relative to Application
        overall_stage_conversion_pct = round((current_count / total_candidates) * 100.0, 1) if total_candidates > 0 else 0.0
        
        # Average duration spent at this stage
        dur_col = f"duration_{stage.lower()}_days"
        avg_duration = round(df[dur_col].mean(), 1) if dur_col in df.columns else 0.0
        
        funnel_rows.append({
            "stage_order": idx + 1,
            "stage": stage,
            "candidate_count": current_count,
            "overall_conversion_pct": overall_stage_conversion_pct,
            "next_stage": next_stage,
            "next_stage_count": next_count,
            "stage_conversion_pct": conversion_pct,
            "stage_dropoff_pct": dropoff_pct,
            "candidates_dropped_at_stage": dropoff_count,
            "avg_duration_days": avg_duration
        })
        
    df_funnel = pd.DataFrame(funnel_rows)
    
    # Save funnel CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "recruitment_funnel_summary.csv")
    df_funnel.to_csv(dest_csv, index=False)
    
    dest_json = os.path.join(DEST_DIR, "recruitment_funnel_summary.json")
    with open(dest_json, "w") as f:
        json.dump(df_funnel.to_dict(orient="records"), f, indent=2)
        
    print(f" Saved Recruitment Funnel Summary: {dest_csv}\n")
    print(df_funnel.to_string(index=False))
    print("\n Recruitment Funnel Aggregation Complete Successfully!")

if __name__ == "__main__":
    calculate_funnel()
