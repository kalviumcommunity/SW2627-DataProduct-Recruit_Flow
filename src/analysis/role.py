import os
import json
import pandas as pd
import numpy as np

# Use paths relative to workspace root or using os.path logic to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

def calculate_role_analytics():
    print("="*60)
    print(" STARTING ROLE-WISE DROP-OFF RATES & METRICS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df = pd.read_csv(SRC_FEATURES)
    
    # 1. Calculate department-level drop-off rates to compare against
    dept_stats = {}
    for dept_name, group in df.groupby('department'):
        dept_total = len(group)
        dept_dropped = group['dropped'].sum()
        dept_stats[dept_name] = round((dept_dropped / dept_total) * 100.0, 2) if dept_total > 0 else 0.0
        
    # 2. Group by department AND role
    role_groups = df.groupby(['department', 'role'])
    
    role_rows = []
    for (dept_name, role_name), group in role_groups:
        total_candidates = len(group)
        dropped_candidates = int(group['dropped'].sum())
        joined_candidates = int(group['joined'].sum())
        dropoff_rate = round((dropped_candidates / total_candidates) * 100.0, 2) if total_candidates > 0 else 0.0
        
        dept_avg = dept_stats.get(dept_name, 0.0)
        delta = round(dropoff_rate - dept_avg, 2)
        
        role_rows.append({
            "department": dept_name,
            "role": role_name,
            "total_candidates": total_candidates,
            "dropped_candidates": dropped_candidates,
            "joined_candidates": joined_candidates,
            "role_dropoff_rate": dropoff_rate,
            "department_average_dropoff_rate": dept_avg,
            "delta_from_department_average": delta
        })
        
    df_role = pd.DataFrame(role_rows)
    
    # Sort for readability: group by department, and order by highest drop-off rate
    df_role = df_role.sort_values(by=['department', 'role_dropoff_rate'], ascending=[True, False])
    
    # Save CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "role_analysis_summary.csv")
    df_role.to_csv(dest_csv, index=False)
    
    dest_json = os.path.join(DEST_DIR, "role_analysis_summary.json")
    with open(dest_json, "w") as f:
        json.dump(df_role.to_dict(orient="records"), f, indent=2)
        
    print(f" Saved Role Analysis Summary: {dest_csv}\n")
    print(df_role.to_string(index=False))
    print("\n Role Analysis Aggregation Completed Successfully!")

if __name__ == "__main__":
    calculate_role_analytics()
