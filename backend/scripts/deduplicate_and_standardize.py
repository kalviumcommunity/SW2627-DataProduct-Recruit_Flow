import os
import glob
import pandas as pd
from datetime import datetime

SRC_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_clean"
DEST_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets_final"

def parse_iso_date(val):
    if pd.isna(val) or val is None or str(val).strip() in ['', 'nan', 'None']:
        return None
    try:
        dt = pd.to_datetime(val, errors='coerce')
        if pd.isna(dt):
            return None
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None

def process_candidates(df):
    df = df.copy()
    initial_len = len(df)
    
    # Standardize date
    if 'application_date' in df.columns:
        df['application_date'] = df['application_date'].apply(parse_iso_date)
        
    # Deduplicate: exact candidate_id
    df = df.drop_duplicates(subset=['candidate_id'], keep='first')
    
    removed = initial_len - len(df)
    print(f"Candidates: Removed {removed} genuine duplicate candidate IDs. Final count: {len(df)}")
    return df

def process_stages(df):
    df = df.copy()
    initial_len = len(df)
    
    # Standardize dates
    for date_col in ['stage_entry_date', 'stage_exit_date']:
        if date_col in df.columns:
            df[date_col] = df[date_col].apply(parse_iso_date)
            
    # Chronological sanity check & swap if inverted
    valid_dates_mask = df['stage_entry_date'].notnull() & df['stage_exit_date'].notnull()
    inverted_mask = valid_dates_mask & (df['stage_entry_date'] > df['stage_exit_date'])
    if inverted_mask.sum() > 0:
        print(f"Stages: Fixed {inverted_mask.sum()} inverted date pairs (entry > exit).")
        # Swap entry and exit
        df.loc[inverted_mask, ['stage_entry_date', 'stage_exit_date']] = df.loc[inverted_mask, ['stage_exit_date', 'stage_entry_date']].values
        
    # Genuine Duplicates: Same candidate_id + stage + stage_entry_date
    df = df.drop_duplicates(subset=['candidate_id', 'stage', 'stage_entry_date'], keep='first')
    
    removed = initial_len - len(df)
    print(f"Stages: Removed {removed} exact duplicate stage event rows. Legitimate stage history preserved: {len(df)} rows.")
    return df

def process_interviews(df):
    df = df.copy()
    initial_len = len(df)
    
    # Standardize date
    if 'interview_date' in df.columns:
        df['interview_date'] = df['interview_date'].apply(parse_iso_date)
        
    # Genuine Duplicates: Exact interview_id
    if 'interview_id' in df.columns:
        df = df.drop_duplicates(subset=['interview_id'], keep='first')
        
    removed = initial_len - len(df)
    print(f"Interviews: Removed {removed} genuine duplicate interview IDs. Final count: {len(df)}")
    return df

def process_onboarding(df):
    df = df.copy()
    initial_len = len(df)
    
    # Standardize dates
    for date_col in ['offer_date', 'expected_joining_date', 'actual_joining_date']:
        if date_col in df.columns:
            df[date_col] = df[date_col].apply(parse_iso_date)
            
    # Deduplicate: exact candidate_id
    df = df.drop_duplicates(subset=['candidate_id'], keep='first')
    
    removed = initial_len - len(df)
    print(f"Onboarding: Removed {removed} duplicate onboarding rows. Final count: {len(df)}")
    return df

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    processors = {
        'candidates.csv': process_candidates,
        'recruitment_stages.csv': process_stages,
        'interviews.csv': process_interviews,
        'onboarding.csv': process_onboarding
    }
    
    print("Executing Deduplication & Date Standardization...\n")
    for file_name, proc_fn in processors.items():
        src_path = os.path.join(SRC_DIR, file_name)
        if not os.path.exists(src_path):
            print(f"Skipping {file_name} - file not found.")
            continue
            
        print(f"Processing: {file_name}...")
        df_raw = pd.read_csv(src_path)
        df_proc = proc_fn(df_raw)
        
        dest_path = os.path.join(DEST_DIR, file_name)
        df_proc.to_csv(dest_path, index=False)
        print(f"Saved processed file to: {dest_path}\n")
        
    print("Deduplication & Date Standardization Complete!")

if __name__ == "__main__":
    main()
