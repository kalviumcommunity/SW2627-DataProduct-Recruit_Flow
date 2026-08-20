import os
import glob
import pandas as pd
import json
from datetime import datetime

SRC_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_normalized"
DEST_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_integrated"

STAGE_ORDER = ["Application", "Screening", "Interview", "Offer", "Joined"]

def calculate_duration(entry_str, exit_str):
    if not entry_str or not exit_str or pd.isna(entry_str) or pd.isna(exit_str):
        return 0
    try:
        d1 = datetime.strptime(str(entry_str), "%Y-%m-%d")
        d2 = datetime.strptime(str(exit_str), "%Y-%m-%d")
        delta = (d2 - d1).days
        return max(0, delta)
    except Exception:
        return 0

def build_journeys():
    print("="*60)
    print(" STARTING CANDIDATE JOURNEY RECONSTRUCTION & DATA INTEGRATION")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Load 4 normalized datasets
    cand_df = pd.read_csv(os.path.join(SRC_DIR, "candidates.csv"))
    stages_df = pd.read_csv(os.path.join(SRC_DIR, "recruitment_stages.csv"))
    interviews_df = pd.read_csv(os.path.join(SRC_DIR, "interviews.csv"))
    onboarding_df = pd.read_csv(os.path.join(SRC_DIR, "onboarding.csv"))
    
    # Index helper lookup tables by candidate_id
    interviews_by_cand = {}
    if not interviews_df.empty and 'candidate_id' in interviews_df.columns:
        for _, row in interviews_df.iterrows():
            cid = row['candidate_id']
            if cid not in interviews_by_cand:
                interviews_by_cand[cid] = []
            interviews_by_cand[cid].append(row.to_dict())
            
    onboarding_by_cand = {}
    if not onboarding_df.empty and 'candidate_id' in onboarding_df.columns:
        for _, row in onboarding_df.iterrows():
            cid = row['candidate_id']
            onboarding_by_cand[cid] = row.to_dict()

    stages_by_cand = {}
    if not stages_df.empty and 'candidate_id' in stages_df.columns:
        for _, row in stages_df.iterrows():
            cid = row['candidate_id']
            if cid not in stages_by_cand:
                stages_by_cand[cid] = []
            stages_by_cand[cid].append(row.to_dict())

    journeys_json = []
    flattened_rows = []
    
    for _, cand in cand_df.iterrows():
        cid = cand['candidate_id']
        c_stages = stages_by_cand.get(cid, [])
        c_interviews = interviews_by_cand.get(cid, [])
        c_onboarding = onboarding_by_cand.get(cid, {})
        
        # Sort stages chronologically
        c_stages = sorted(c_stages, key=lambda x: (x.get('stage_entry_date') or '', STAGE_ORDER.index(x.get('stage')) if x.get('stage') in STAGE_ORDER else 99))
        
        timeline = []
        furthest_stage = "Application"
        final_outcome = "In Progress"
        total_time_in_pipeline = 0
        
        for stg in c_stages:
            stage_name = stg.get('stage')
            entry_d = stg.get('stage_entry_date')
            exit_d = stg.get('stage_exit_date')
            dur = calculate_duration(entry_d, exit_d)
            total_time_in_pipeline += dur
            status = stg.get('status')
            reason = stg.get('rejection_reason')
            
            # Update furthest stage
            if stage_name in STAGE_ORDER:
                if STAGE_ORDER.index(stage_name) > STAGE_ORDER.index(furthest_stage):
                    furthest_stage = stage_name
                    
            event_obj = {
                "stage": stage_name,
                "raw_stage_name": stg.get('stage_raw'),
                "entry_date": entry_d,
                "exit_date": exit_d,
                "duration_days": dur,
                "status": status,
                "rejection_reason": reason
            }
            
            # Enrich with interview data if this is the Interview stage
            if stage_name == "Interview" and c_interviews:
                event_obj["interviews"] = c_interviews
                
            # Enrich with onboarding data if this is Offer or Joined stage
            if stage_name in ["Offer", "Joined"] and c_onboarding:
                event_obj["onboarding_details"] = {
                    "offer_date": c_onboarding.get('offer_date'),
                    "offer_status": c_onboarding.get('offer_status'),
                    "joining_status": c_onboarding.get('joining_status'),
                    "actual_joining_date": c_onboarding.get('actual_joining_date')
                }
                
            timeline.append(event_obj)
            
            # Determine outcome
            if status in ['Rejected', 'Withdrawn', 'No-show']:
                final_outcome = f"Dropped at {stage_name}"
            elif stage_name == "Joined" and status in ['Completed', 'Passed']:
                final_outcome = "Hired & Joined"
                
        candidate_journey = {
            "candidate_id": cid,
            "department": cand.get('department'),
            "role": cand.get('role'),
            "application_date": cand.get('application_date'),
            "source": cand.get('source'),
            "experience_years": int(cand.get('experience_years', 0)),
            "location": cand.get('location'),
            "furthest_stage_reached": furthest_stage,
            "final_outcome": final_outcome,
            "total_pipeline_days": total_time_in_pipeline,
            "timeline": timeline
        }
        journeys_json.append(candidate_journey)
        
        # Build flattened row for analytics CSV
        flat_row = {
            "candidate_id": cid,
            "department": cand.get('department'),
            "role": cand.get('role'),
            "application_date": cand.get('application_date'),
            "source": cand.get('source'),
            "experience_years": cand.get('experience_years'),
            "location": cand.get('location'),
            "furthest_stage_reached": furthest_stage,
            "final_outcome": final_outcome,
            "total_pipeline_days": total_time_in_pipeline,
            "num_stages_completed": len(timeline),
            "rejection_reason": timeline[-1].get('rejection_reason') if timeline and final_outcome.startswith('Dropped') else None
        }
        flattened_rows.append(flat_row)
        
    # Save unified JSON (cleaning NaN to None for strict JSON compatibility)
    json_path = os.path.join(DEST_DIR, "candidate_journeys.json")
    def sanitize_obj(obj):
        if isinstance(obj, dict):
            return {k: sanitize_obj(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_obj(v) for v in obj]
        elif pd.isna(obj):
            return None
        return obj

    with open(json_path, "w") as f:
        json.dump(sanitize_obj(journeys_json), f, indent=2)
    print(f" Saved unified Candidate Journey JSON: {json_path}")

    
    # Save flattened CSV
    flat_df = pd.DataFrame(flattened_rows)
    csv_path = os.path.join(DEST_DIR, "candidate_journeys.csv")
    flat_df.to_csv(csv_path, index=False)
    print(f" Saved flattened Candidate Journey CSV: {csv_path}")

    print("\n Candidate Journey Reconstruction Complete!")

if __name__ == "__main__":
    build_journeys()
