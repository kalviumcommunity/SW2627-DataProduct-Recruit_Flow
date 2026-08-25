import os
import json
import pandas as pd
import numpy as np

# Use paths relative to workspace root or using os.path logic to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
SRC_STAGES = os.path.join(BASE_DIR, "data", "processed", "recruitment_stages.csv")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

STAGE_ORDER = ["Application", "Screening", "Interview", "Offer", "Joined"]

def calculate_stage_durations():
    print("="*60)
    print(" STARTING STAGE DURATION & HIRING VELOCITY ANALYSIS")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df_features = pd.read_csv(SRC_FEATURES)
    
    # 1. Per-stage duration statistics
    # Compute duration metrics per stage based on candidates who actively passed through that stage
    stage_rows = []
    
    for idx, stage in enumerate(STAGE_ORDER):
        dur_col = f"duration_{stage.lower()}_days"
        
        # Candidates who reached at least this stage
        candidates_in_stage = df_features[df_features['furthest_stage_index'] >= idx]
        count = len(candidates_in_stage)
        
        if count > 0 and dur_col in df_features.columns:
            durations = candidates_in_stage[dur_col].dropna()
            avg_days = round(float(durations.mean()), 2)
            med_days = round(float(durations.median()), 2)
            min_days = int(durations.min()) if not durations.empty else 0
            max_days = int(durations.max()) if not durations.empty else 0
            std_days = round(float(durations.std()), 2) if len(durations) > 1 else 0.0
            p75_days = round(float(durations.quantile(0.75)), 2) if not durations.empty else 0.0
        else:
            avg_days = 0.0
            med_days = 0.0
            min_days = 0
            max_days = 0
            std_days = 0.0
            p75_days = 0.0
            
        stage_rows.append({
            "stage_order": idx + 1,
            "stage": stage,
            "candidates_count": count,
            "avg_duration_days": avg_days,
            "median_duration_days": med_days,
            "min_duration_days": min_days,
            "max_duration_days": max_days,
            "std_duration_days": std_days,
            "p75_duration_days": p75_days
        })
        
    df_stages = pd.DataFrame(stage_rows)
    
    # Identify bottlenecks: stages with average duration >= overall average or top latency
    avg_stage_time = df_stages['avg_duration_days'].mean()
    df_stages['is_bottleneck'] = df_stages['avg_duration_days'] >= avg_stage_time
    df_stages['bottleneck_severity'] = df_stages.apply(
        lambda r: 'High' if r['avg_duration_days'] > avg_stage_time * 1.5
        else ('Medium' if r['is_bottleneck'] else 'Low'),
        axis=1
    )
    
    # 2. Department-level velocity breakdown
    dept_rows = []
    for dept_name, group in df_features.groupby('department'):
        total_cand = len(group)
        joined_cand = group[group['joined'] == 1]
        dropped_cand = group[group['dropped'] == 1]
        
        avg_total_dur = round(float(group['total_recruitment_duration_days'].mean()), 2)
        med_total_dur = round(float(group['total_recruitment_duration_days'].median()), 2)
        
        time_to_hire = round(float(joined_cand['total_recruitment_duration_days'].mean()), 2) if not joined_cand.empty else None
        time_to_drop = round(float(dropped_cand['total_recruitment_duration_days'].mean()), 2) if not dropped_cand.empty else None
        delayed_drops = int(group['is_delayed_dropoff'].sum()) if 'is_delayed_dropoff' in group.columns else 0
        
        dept_rows.append({
            "department": dept_name,
            "total_candidates": total_cand,
            "avg_pipeline_duration_days": avg_total_dur,
            "median_pipeline_duration_days": med_total_dur,
            "avg_time_to_hire_days": time_to_hire,
            "avg_time_to_drop_days": time_to_drop,
            "delayed_dropoffs_count": delayed_drops
        })
        
    df_dept_velocity = pd.DataFrame(dept_rows)
    
    # 3. Overall Outcome Velocity (Hired vs Dropped)
    hired = df_features[df_features['joined'] == 1]
    dropped = df_features[df_features['dropped'] == 1]
    delayed_dropped_count = int(df_features['is_delayed_dropoff'].sum()) if 'is_delayed_dropoff' in df_features.columns else 0
    
    outcome_velocity = {
        "overall_time_to_hire": {
            "hired_candidates_count": len(hired),
            "avg_days": round(float(hired['total_recruitment_duration_days'].mean()), 2) if not hired.empty else 0.0,
            "median_days": round(float(hired['total_recruitment_duration_days'].median()), 2) if not hired.empty else 0.0,
            "min_days": int(hired['total_recruitment_duration_days'].min()) if not hired.empty else 0,
            "max_days": int(hired['total_recruitment_duration_days'].max()) if not hired.empty else 0
        },
        "overall_time_to_drop": {
            "dropped_candidates_count": len(dropped),
            "avg_days": round(float(dropped['total_recruitment_duration_days'].mean()), 2) if not dropped.empty else 0.0,
            "median_days": round(float(dropped['total_recruitment_duration_days'].median()), 2) if not dropped.empty else 0.0,
            "min_days": int(dropped['total_recruitment_duration_days'].min()) if not dropped.empty else 0,
            "max_days": int(dropped['total_recruitment_duration_days'].max()) if not dropped.empty else 0
        },
        "delayed_dropoffs": {
            "count": delayed_dropped_count,
            "percentage_of_dropped": round((delayed_dropped_count / len(dropped)) * 100.0, 2) if len(dropped) > 0 else 0.0
        }
    }
    
    # 4. Bottleneck Insights Summary
    slowest_stage = df_stages.loc[df_stages['avg_duration_days'].idxmax()]['stage']
    max_avg_stage_days = df_stages['avg_duration_days'].max()
    
    bottleneck_summary = {
        "primary_bottleneck_stage": slowest_stage,
        "max_average_stage_duration_days": max_avg_stage_days,
        "average_stage_duration_benchmark_days": round(avg_stage_time, 2),
        "flagged_bottleneck_stages": df_stages[df_stages['is_bottleneck']]['stage'].tolist()
    }
    
    # Structured JSON payload
    full_payload = {
        "stage_metrics": df_stages.to_dict(orient="records"),
        "department_velocity": df_dept_velocity.to_dict(orient="records"),
        "outcome_velocity": outcome_velocity,
        "bottleneck_insights": bottleneck_summary
    }
    
    # Save CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "stage_duration_summary.csv")
    df_stages.to_csv(dest_csv, index=False)
    
    dest_json = os.path.join(DEST_DIR, "stage_duration_summary.json")
    with open(dest_json, "w") as f:
        json.dump(full_payload, f, indent=2)
        
    print(f" Saved Stage Duration Summary (CSV): {dest_csv}")
    print(f" Saved Stage Duration Full Summary (JSON): {dest_json}\n")
    print("--- Stage-wise Duration & Bottlenecks ---")
    print(df_stages.to_string(index=False))
    print("\n--- Department Velocity Breakdown ---")
    print(df_dept_velocity.to_string(index=False))
    print("\n--- Bottleneck Insights ---")
    print(json.dumps(bottleneck_summary, indent=2))
    print("\n Stage Duration & Hiring Velocity Analysis Completed Successfully!")

if __name__ == "__main__":
    calculate_stage_durations()
