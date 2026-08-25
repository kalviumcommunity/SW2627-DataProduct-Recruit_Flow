import os
import json
import pandas as pd
import numpy as np

# Use paths relative to workspace root or using os.path logic to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

def calculate_department_analytics():
    print("="*60)
    print(" STARTING DEPARTMENT-WISE DROP-OFF RATES & METRICS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df = pd.read_csv(SRC_FEATURES)
    
    # 1. Company average drop-off rate
    company_total = len(df)
    company_dropped = df['dropped'].sum()
    company_joined = df['joined'].sum()
    company_dropoff_rate = round((company_dropped / company_total) * 100.0, 2) if company_total > 0 else 0.0
    
    # 2. Group by department
    dept_groups = df.groupby('department')
    
    dept_rows = []
    for dept_name, group in dept_groups:
        total_candidates = len(group)
        dropped_candidates = int(group['dropped'].sum())
        joined_candidates = int(group['joined'].sum())
        dropoff_rate = round((dropped_candidates / total_candidates) * 100.0, 2) if total_candidates > 0 else 0.0
        delta = round(dropoff_rate - company_dropoff_rate, 2)
        
        dept_rows.append({
            "department": dept_name,
            "total_candidates": total_candidates,
            "dropped_candidates": dropped_candidates,
            "joined_candidates": joined_candidates,
            "dropoff_rate": dropoff_rate,
            "company_average_dropoff_rate": company_dropoff_rate,
            "delta_from_company_average": delta
        })
        
    df_dept = pd.DataFrame(dept_rows)
    
    # Save CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "department_analysis_summary.csv")
    df_dept.to_csv(dest_csv, index=False)
    
    dest_json = os.path.join(DEST_DIR, "department_analysis_summary.json")
    with open(dest_json, "w") as f:
        json.dump(df_dept.to_dict(orient="records"), f, indent=2)
        
    print(f" Saved Department Analysis Summary: {dest_csv}\n")
    print(df_dept.to_string(index=False))
    print("\n Department Analysis Aggregation Completed Successfully!")

if __name__ == "__main__":
    calculate_department_analytics()
