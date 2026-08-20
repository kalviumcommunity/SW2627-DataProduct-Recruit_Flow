import os
import glob
import pandas as pd
import json

SRC_DIR = r"data/processed"


def validate_datasets():
    print("="*60)
    print(" STARTING DATA VALIDATION (LOGICAL SANITY CHECKS)")
    print("="*60)
    
    # Load normalized files
    candidates_path = os.path.join(SRC_DIR, "candidates.csv")
    stages_path = os.path.join(SRC_DIR, "recruitment_stages.csv")
    interviews_path = os.path.join(SRC_DIR, "interviews.csv")
    onboarding_path = os.path.join(SRC_DIR, "onboarding.csv")
    
    df_cand = pd.read_csv(candidates_path) if os.path.exists(candidates_path) else pd.DataFrame()
    df_stages = pd.read_csv(stages_path) if os.path.exists(stages_path) else pd.DataFrame()
    df_interviews = pd.read_csv(interviews_path) if os.path.exists(interviews_path) else pd.DataFrame()
    df_onboarding = pd.read_csv(onboarding_path) if os.path.exists(onboarding_path) else pd.DataFrame()
    
    valid_candidate_ids = set(df_cand['candidate_id'].dropna().unique()) if not df_cand.empty else set()
    errors = []
    
    # ----------------------------------------------------
    # Rule 5: Candidate ID existence (Referential Integrity)
    # ----------------------------------------------------
    print("\n1. Checking Rule 5: Referential Integrity (Candidate ID Existence)...")
    for name, df in [('recruitment_stages', df_stages), ('interviews', df_interviews), ('onboarding', df_onboarding)]:
        if not df.empty and 'candidate_id' in df.columns:
            orphan_mask = ~df['candidate_id'].isin(valid_candidate_ids)
            orphans = df[orphan_mask]
            if not orphans.empty:
                for idx, row in orphans.iterrows():
                    err = f"Rule 5 Violation [{name} row {idx}]: Candidate ID '{row['candidate_id']}' not found in candidates list."
                    errors.append(err)
                    print(f"   [FAIL] {err}")
            else:
                print(f"   [OK] All candidate IDs in {name} exist in candidates list.")

    # ----------------------------------------------------
    # Rule 4: Score boundaries (0 <= score <= 10)
    # ----------------------------------------------------
    print("\n2. Checking Rule 4: Interview Score Boundaries (0 <= score <= 10)...")
    if not df_interviews.empty:
        score_cols = [c for c in ['technical_score', 'communication_score', 'overall_score'] if c in df_interviews.columns]
        invalid_scores_count = 0
        for idx, row in df_interviews.iterrows():
            for sc in score_cols:
                val = row[sc]
                if pd.notnull(val):
                    if val < 0.0 or val > 10.0:
                        err = f"Rule 4 Violation [interviews row {idx}]: {sc} = {val} is out of bounds [0, 10]."
                        errors.append(err)
                        invalid_scores_count += 1
                        print(f"   [FAIL] {err}")
        if invalid_scores_count == 0:
            print("   [OK] All interview scores are within valid bounds [0, 10].")

    # ----------------------------------------------------
    # Rule 1 & Rule 2: Stage Entry/Exit Timeline Sanity
    # ----------------------------------------------------
    print("\n3. Checking Rule 1 & Rule 2: Stage Timeline Logic...")
    if not df_stages.empty:
        # Merge application_date from candidates
        app_dates = df_cand.set_index('candidate_id')['application_date'].to_dict() if not df_cand.empty else {}
        
        rule1_errors = 0
        rule2_errors = 0
        for idx, row in df_stages.iterrows():
            cid = row['candidate_id']
            entry = row['stage_entry_date']
            exit_d = row['stage_exit_date']
            
            # Rule 1: application_date <= stage_entry_date
            app_d = app_dates.get(cid)
            if app_d and pd.notnull(entry):
                if entry < app_d:
                    err = f"Rule 1 Violation [recruitment_stages row {idx}]: Stage entry date '{entry}' is before application date '{app_d}' for candidate '{cid}'."
                    errors.append(err)
                    rule1_errors += 1
                    print(f"   [FAIL] {err}")
                    
            # Rule 2: stage_entry_date <= stage_exit_date
            if pd.notnull(entry) and pd.notnull(exit_d):
                if exit_d < entry:
                    err = f"Rule 2 Violation [recruitment_stages row {idx}]: Stage exit date '{exit_d}' is before entry date '{entry}' for candidate '{cid}'."
                    errors.append(err)
                    rule2_errors += 1
                    print(f"   [FAIL] {err}")
                    
        if rule1_errors == 0:
            print("   [OK] Rule 1 Passed: All stage entry dates happen on or after application date.")
        if rule2_errors == 0:
            print("   [OK] Rule 2 Passed: All stage exit dates happen on or after stage entry date.")

    # ----------------------------------------------------
    # Rule 3: Offer date <= Actual joining date
    # ----------------------------------------------------
    print("\n4. Checking Rule 3: Offer & Joining Timeline Logic...")
    if not df_onboarding.empty:
        rule3_errors = 0
        for idx, row in df_onboarding.iterrows():
            offer_d = row.get('offer_date')
            actual_j = row.get('actual_joining_date')
            cid = row['candidate_id']
            
            if pd.notnull(offer_d) and pd.notnull(actual_j):
                if actual_j < offer_d:
                    err = f"Rule 3 Violation [onboarding row {idx}]: Actual joining date '{actual_j}' is before offer date '{offer_d}' for candidate '{cid}'."
                    errors.append(err)
                    rule3_errors += 1
                    print(f"   [FAIL] {err}")
        if rule3_errors == 0:
            print("   [OK] Rule 3 Passed: All joining dates happen on or after offer dates.")

    # ----------------------------------------------------
    # Validation Summary Report
    # ----------------------------------------------------
    print("\n" + "="*60)
    print(" VALIDATION SUMMARY REPORT")
    print("="*60)
    print(f"Total Rules Tested : 5")
    print(f"Total Violations   : {len(errors)}")
    if len(errors) == 0:
        print("Status             : PASSED ALL VALIDATION RULES!")
    else:
        print("Status             : FAILED WITH VIOLATIONS")

if __name__ == "__main__":
    validate_datasets()

