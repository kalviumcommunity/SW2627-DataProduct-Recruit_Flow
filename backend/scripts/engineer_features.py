import os
import glob
import json
import pandas as pd
import numpy as np

SRC_JSON = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_integrated\candidate_journeys.json"
DEST_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_features"

STAGE_ORDER = ["Application", "Screening", "Interview", "Offer", "Joined"]

def engineer_features():
    print("="*60)
    print(" STARTING FEATURE ENGINEERING (VARIABLE CREATION)")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_JSON):
        print(f"Error: {SRC_JSON} not found. Run step 5 first.")
        return
        
    with open(SRC_JSON, "r") as f:
        journeys = json.load(f)
        
    feature_rows = []
    
    for c in journeys:
        cid = c['candidate_id']
        dept = c.get('department')
        role = c.get('role')
        app_date = c.get('application_date')
        source = c.get('source')
        exp = c.get('experience_years')
        loc = c.get('location')
        furthest = c.get('furthest_stage_reached', 'Application')
        outcome = c.get('final_outcome', '')
        
        timeline = c.get('timeline', [])
        
        # 1. Total recruitment duration
        total_duration = c.get('total_pipeline_days', 0)
        
        # 2. Binary Target: dropped (1 if candidate dropped off, 0 if hired & joined)
        joined_flag = 1 if outcome == "Hired & Joined" else 0
        dropped_flag = 0 if joined_flag == 1 else 1
        
        # 3. Binary Targets: offer_accepted and joined
        offer_accepted_flag = 0
        joining_status_flag = 0
        
        # 4. Extract stage-specific durations
        stage_durations = {f"duration_{stg.lower()}_days": 0 for stg in STAGE_ORDER}
        rejection_reason = None
        interview_scores = []
        
        for event in timeline:
            stg = event.get('stage')
            dur = event.get('duration_days', 0)
            if stg in STAGE_ORDER:
                stage_durations[f"duration_{stg.lower()}_days"] = dur
                
            if event.get('status') in ['Rejected', 'Withdrawn', 'No-show'] and event.get('rejection_reason'):
                rejection_reason = event.get('rejection_reason')
                
            # Collect interview scores
            if 'interviews' in event:
                for iv in event['interviews']:
                    if 'overall_score' in iv and iv['overall_score'] is not None:
                        interview_scores.append(float(iv['overall_score']))
                        
            # Check offer details
            if 'onboarding_details' in event:
                ob = event['onboarding_details']
                if ob.get('offer_status') == 'Accepted':
                    offer_accepted_flag = 1
                if ob.get('joining_status') == 'Joined':
                    joining_status_flag = 1
                    
        # 5. Calculate average interview score
        avg_interview_score = float(np.mean(interview_scores)) if interview_scores else np.nan
        
        # 6. Furthest stage numerical index (0 to 4)
        furthest_index = STAGE_ORDER.index(furthest) if furthest in STAGE_ORDER else 0
        
        row = {
            "candidate_id": cid,
            "department": dept,
            "role": role,
            "application_date": app_date,
            "source": source,
            "experience_years": exp,
            "location": loc,
            "furthest_stage_reached": furthest,
            "furthest_stage_index": furthest_index,
            "final_outcome": outcome,
            "total_recruitment_duration_days": total_duration,
            "dropped": dropped_flag,
            "joined": joining_status_flag,
            "offer_accepted": offer_accepted_flag,
            "average_interview_score": round(avg_interview_score, 2) if pd.notnull(avg_interview_score) else None,
            "rejection_reason": rejection_reason,
            "duration_application_days": stage_durations["duration_application_days"],
            "duration_screening_days": stage_durations["duration_screening_days"],
            "duration_interview_days": stage_durations["duration_interview_days"],
            "duration_offer_days": stage_durations["duration_offer_days"],
            "duration_joined_days": stage_durations["duration_joined_days"]
        }
        feature_rows.append(row)
        
    df_features = pd.DataFrame(feature_rows)
    
    # 7. Derive delayed drop-off flag (Duration > Median for dropped candidates)
    median_interview_duration = df_features['duration_interview_days'].median()
    df_features['is_delayed_dropoff'] = (
        (df_features['dropped'] == 1) & 
        (df_features['duration_interview_days'] > median_interview_duration)
    ).astype(int)
    
    # Save feature matrix
    dest_csv = os.path.join(DEST_DIR, "candidate_features.csv")
    df_features.to_csv(dest_csv, index=False)
    print(f" Saved Engineered Feature Matrix ({len(df_features)} rows x {len(df_features.columns)} cols): {dest_csv}\n")
    
    print("Engineered Features Sample:")
    print(df_features[['candidate_id', 'department', 'furthest_stage_reached', 'total_recruitment_duration_days', 'average_interview_score', 'dropped', 'joined']].to_string(index=False))

    print("\n Feature Engineering Complete Successfully!")

if __name__ == "__main__":
    engineer_features()
