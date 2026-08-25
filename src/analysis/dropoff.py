import os
import json
import pandas as pd
import numpy as np

# Use paths relative to workspace root or using os.path logic to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

def calculate_dropoff():
    print("="*60)
    print(" STARTING DROP-OFF REASON CROSS-TABULATION ANALYSIS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df = pd.read_csv(SRC_FEATURES)
    
    # Filter for candidates who dropped
    df_dropped = df[df['dropped'] == 1].copy()
    
    # Impute missing reason with 'Unspecified Drop-off' if null
    df_dropped['rejection_reason'] = df_dropped['rejection_reason'].fillna('Unspecified Drop-off')
    
    # Ensure column naming consistency
    df_dropped = df_dropped.rename(columns={'furthest_stage_reached': 'stage'})
    
    # 1. Detailed breakdown (Department + Stage + Reason)
    detailed_df = df_dropped.groupby(['department', 'stage', 'rejection_reason']).size().reset_index(name='count')
    detailed_df = detailed_df.sort_values(by=['department', 'stage', 'count'], ascending=[True, True, False])
    
    # 2. Department cross-tabulation
    dept_ct = pd.crosstab(df_dropped['department'], df_dropped['rejection_reason']).reset_index()
    
    # 3. Stage cross-tabulation
    stage_ct = pd.crosstab(df_dropped['stage'], df_dropped['rejection_reason']).reset_index()
    
    # Prepare JSON structure
    json_data = {
        "detailed_reasons": detailed_df.to_dict(orient="records"),
        "department_reasons": dept_ct.to_dict(orient="records"),
        "stage_reasons": stage_ct.to_dict(orient="records")
    }
    
    # Save CSV (detailed breakdown)
    dest_csv = os.path.join(DEST_DIR, "dropoff_analysis_summary.csv")
    detailed_df.to_csv(dest_csv, index=False)
    
    # Save JSON
    dest_json = os.path.join(DEST_DIR, "dropoff_analysis_summary.json")
    with open(dest_json, "w") as f:
        json.dump(json_data, f, indent=2)
        
    print(f" Saved Drop-off Detailed Analysis Summary (CSV): {dest_csv}")
    print(f" Saved Drop-off Full Analysis Summary (JSON): {dest_json}\n")
    print("--- Detailed Reasons Breakdown ---")
    print(detailed_df.to_string(index=False))
    print("\n--- Department Cross-tabulation ---")
    print(dept_ct.to_string(index=False))
    print("\n--- Stage Cross-tabulation ---")
    print(stage_ct.to_string(index=False))
    
    print("\n Drop-off Reason Cross-Tabulation Completed Successfully!")

if __name__ == "__main__":
    calculate_dropoff()
