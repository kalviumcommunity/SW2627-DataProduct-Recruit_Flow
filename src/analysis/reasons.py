import os
import json
import pandas as pd
import numpy as np

# Use paths relative to workspace root or using os.path logic to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

def calculate_reasons():
    print("="*60)
    print(" STARTING DROP-OFF REASON AGGREGATION & METRICS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df = pd.read_csv(SRC_FEATURES)
    
    # Filter for candidates who dropped and have a rejection reason
    df_rejection = df[df['dropped'] == 1].copy()
    
    # Impute missing reason with 'Unspecified Drop-off' if null
    df_rejection['rejection_reason'] = df_rejection['rejection_reason'].fillna('Unspecified Drop-off')
    
    total_dropped = len(df_rejection)
    print(f"Total Dropped Candidates: {total_dropped}")
    
    reason_groups = df_rejection.groupby('rejection_reason')
    
    reason_rows = []
    for reason_name, group in reason_groups:
        count = len(group)
        percentage = round((count / total_dropped) * 100.0, 2) if total_dropped > 0 else 0.0
        
        reason_rows.append({
            "reason": reason_name,
            "count": count,
            "value": count,  # count mapped to value for frontend compatibility
            "percentage": percentage
        })
        
    df_reasons = pd.DataFrame(reason_rows)
    
    if not df_reasons.empty:
        df_reasons = df_reasons.sort_values(by='count', ascending=False)
    
    # Save CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "reasons_analysis_summary.csv")
    df_reasons.to_csv(dest_csv, index=False)
    
    dest_json = os.path.join(DEST_DIR, "reasons_analysis_summary.json")
    with open(dest_json, "w") as f:
        json.dump(df_reasons.to_dict(orient="records"), f, indent=2)
        
    print(f" Saved Reasons Analysis Summary: {dest_csv}\n")
    print(df_reasons.to_string(index=False))
    print("\n Drop-off Reason Analysis Aggregation Completed Successfully!")

if __name__ == "__main__":
    calculate_reasons()
