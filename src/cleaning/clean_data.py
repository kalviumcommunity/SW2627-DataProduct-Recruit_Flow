import os
import glob
import pandas as pd
import numpy as np

SRC_DIR = r"data/raw"
DEST_DIR = r"data/processed"


# Standard Mappings
DEPARTMENT_MAP = {
    "it": "IT", "information technology": "IT",
    "finance": "Finance", "financial": "Finance",
    "hr": "HR", "human resources": "HR",
    "sales": "Sales", "marketing": "Marketing", "engineering": "Engineering"
}

STAGE_MAP = {
    "application": "Application", "applied": "Application",
    "screening": "Screening", "screen": "Screening",
    "technical interview": "Interview", "tech interview": "Interview", "technical": "Interview",
    "hr interview": "Interview", "sales interview": "Interview", "finance interview": "Interview", "interview": "Interview",
    "offer": "Offer",
    "joining": "Joined", "joined": "Joined"
}

REASON_MAP = {
    "technical mismatch": "Technical Mismatch",
    "insufficient python knowledge": "Technical Mismatch",
    "declined offer - better opportunity elsewhere": "Offer Declined - Better Opportunity",
    "application put on hold; candidate withdrew": "Candidate Withdrew",
    "did not join after accepting offer": "No Show"
}

def clean_candidates(df):
    df = df.copy()
    # Trim strings
    for col in ['candidate_id', 'department', 'role', 'source', 'location']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Standardize department
    df['department'] = df['department'].apply(lambda x: DEPARTMENT_MAP.get(x.lower(), x.title()))
    
    # Missing values: experience_years (Department Median -> Overall Median)
    if 'experience_years' in df.columns:
        df['experience_years'] = pd.to_numeric(df['experience_years'], errors='coerce')
        dept_medians = df.groupby('department')['experience_years'].transform('median')
        overall_median = df['experience_years'].median()
        if pd.isna(overall_median): overall_median = 2.0
        df['experience_years'] = df['experience_years'].fillna(dept_medians).fillna(overall_median).astype(int)
        
    # Missing values: department/role/source/location -> Mode / Unknown
    for col in ['department', 'role', 'source', 'location']:
        if col in df.columns and df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
            df[col] = df[col].fillna(mode_val)
            
    # Dates to ISO YYYY-MM-DD
    if 'application_date' in df.columns:
        df['application_date'] = pd.to_datetime(df['application_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
    return df

def clean_stages(df):
    df = df.copy()
    for col in ['candidate_id', 'stage', 'status', 'rejection_reason', 'next_stage']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': None, 'None': None, '': None})
            
    # Standardize stage
    if 'stage' in df.columns:
        df['stage_raw'] = df['stage']
        df['stage'] = df['stage'].apply(lambda x: STAGE_MAP.get(x.lower(), x.title()) if x else x)
        
    # Standardize rejection reason if rejected
    if 'rejection_reason' in df.columns:
        df['rejection_reason'] = df['rejection_reason'].apply(lambda x: REASON_MAP.get(x.lower(), x.title()) if x else None)
        # Impute missing reason ONLY if status is Rejected/Withdrawn/No-show
        mask_rejected_no_reason = df['status'].isin(['Rejected', 'No-show', 'Withdrawn']) & df['rejection_reason'].isnull()
        df.loc[mask_rejected_no_reason, 'rejection_reason'] = 'Unspecified Drop-off'
        
    # Dates to ISO YYYY-MM-DD
    for date_col in ['stage_entry_date', 'stage_exit_date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
            
    return df

def clean_interviews(df):
    df = df.copy()
    for col in ['interview_id', 'candidate_id', 'stage', 'interviewer', 'recommendation', 'feedback']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Numerical scores: Median Imputation by stage
    for score_col in ['technical_score', 'communication_score']:
        if score_col in df.columns:
            df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
            stage_medians = df.groupby('stage')[score_col].transform('median')
            overall_median = df[score_col].median()
            if pd.isna(overall_median): overall_median = 6.0
            df[score_col] = df[score_col].fillna(stage_medians).fillna(overall_median).astype(int)
            
    # Overall score recalculation / imputation
    if 'technical_score' in df.columns and 'communication_score' in df.columns:
        df['overall_score'] = (df['technical_score'] + df['communication_score']) / 2.0
        
    # Standardize stage
    if 'stage' in df.columns:
        df['stage'] = df['stage'].apply(lambda x: STAGE_MAP.get(x.lower(), x.title()) if x else x)
        
    return df

def clean_onboarding(df):
    df = df.copy()
    for col in ['candidate_id', 'offer_status', 'joining_status', 'onboarding_status']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'nan': None, 'None': None, '': None})
            
    # Dates to ISO YYYY-MM-DD
    for date_col in ['offer_date', 'expected_joining_date', 'actual_joining_date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
            
    # Domain-aware null handling:
    # If offer accepted but joining status is null, set joining status based on actual_joining_date presence
    accepted_mask = (df['offer_status'] == 'Accepted') & df['joining_status'].isnull()
    df.loc[accepted_mask & df['actual_joining_date'].notnull(), 'joining_status'] = 'Joined'
    df.loc[accepted_mask & df['actual_joining_date'].isnull(), 'joining_status'] = 'Pending'
    
    return df

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    cleaners = {
        'candidates.csv': clean_candidates,
        'recruitment_stages.csv': clean_stages,
        'interviews.csv': clean_interviews,
        'onboarding.csv': clean_onboarding
    }
    
    print("Starting Data Cleaning Process...\n")
    for file_name, clean_fn in cleaners.items():
        src_path = os.path.join(SRC_DIR, file_name)
        if not os.path.exists(src_path):
            print(f"Skipping {file_name} - not found.")
            continue
            
        print(f"Cleaning: {file_name}...")
        df_raw = pd.read_csv(src_path)
        df_clean = clean_fn(df_raw)
        
        dest_path = os.path.join(DEST_DIR, file_name)
        df_clean.to_csv(dest_path, index=False)
        print(f"Saved clean dataset to: {dest_path}")

        
    print("\nData Cleaning Completed Successfully!")

if __name__ == "__main__":
    main()
