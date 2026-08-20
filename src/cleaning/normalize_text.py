import os
import glob
import re
import pandas as pd

SRC_DIR = r"data/processed"
DEST_DIR = r"data/processed"


# Categorical Standardization Dictionaries
SOURCE_MAP = {
    "linkedin": "LinkedIn", "linked in": "LinkedIn", "ln": "LinkedIn",
    "indeed": "Indeed",
    "referral": "Referral", "employee referral": "Referral",
    "company website": "Company Website", "careers page": "Company Website", "website": "Company Website",
    "glassdoor": "Glassdoor", "agency": "Recruitment Agency"
}

DEPARTMENT_MAP = {
    "it": "IT", "information technology": "IT", "info tech": "IT", "tech": "IT",
    "engg": "Engineering", "eng": "Engineering", "engineering": "Engineering", "software": "Engineering",
    "finance": "Finance", "financial": "Finance", "accounting": "Finance",
    "hr": "HR", "human resources": "HR", "people": "HR",
    "sales": "Sales", "business development": "Sales",
    "marketing": "Marketing", "ops": "Operations", "operations": "Operations"
}

REASON_MAP = {
    "technical mismatch": "Technical Mismatch", "tech mismatch": "Technical Mismatch",
    "insufficient python knowledge": "Technical Mismatch", "failed technical interview": "Technical Mismatch",
    "salary": "Salary Expectation", "salary expectations too high": "Salary Expectation", "compensation": "Salary Expectation",
    "declined offer - better opportunity elsewhere": "Offer Declined - Better Opportunity",
    "candidate withdrew": "Candidate Withdrew", "application put on hold; candidate withdrew": "Candidate Withdrew",
    "no response": "No Response / Ghosted", "did not join after accepting offer": "No Show"
}

RECOMMENDATION_MAP = {
    "proceed": "Proceed", "pass": "Proceed", "strong hire": "Proceed",
    "reject": "Reject", "no hire": "Reject",
    "hold": "Hold", "maybe": "Hold"
}

def clean_text_val(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    s = re.sub(r'\s+', ' ', s)
    return s if s != '' else None

def normalize_text_col(series, mapping):
    def mapper(val):
        cleaned = clean_text_val(val)
        if not cleaned:
            return None
        lower_val = cleaned.lower()
        if lower_val in mapping:
            return mapping[lower_val]
        return cleaned.title()
    return series.apply(mapper)

def process_candidates(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text_val)
            
    if 'source' in df.columns:
        df['source'] = normalize_text_col(df['source'], SOURCE_MAP)
    if 'department' in df.columns:
        df['department'] = normalize_text_col(df['department'], DEPARTMENT_MAP)
        
    return df

def process_stages(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text_val)
            
    if 'rejection_reason' in df.columns:
        df['rejection_reason'] = df['rejection_reason'].apply(
            lambda x: REASON_MAP.get(x.lower(), x.title()) if x else None
        )
    return df

def process_interviews(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text_val)
            
    if 'recommendation' in df.columns:
        df['recommendation'] = normalize_text_col(df['recommendation'], RECOMMENDATION_MAP)
    return df

def process_onboarding(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text_val)
    return df

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    processors = {
        'candidates.csv': process_candidates,
        'recruitment_stages.csv': process_stages,
        'interviews.csv': process_interviews,
        'onboarding.csv': process_onboarding
    }
    
    print("Executing Text Normalization...\n")
    for file_name, proc_fn in processors.items():
        src_path = os.path.join(SRC_DIR, file_name)
        if not os.path.exists(src_path):
            print(f"Skipping {file_name} - not found.")
            continue
            
        print(f"Normalizing text in: {file_name}...")
        df_raw = pd.read_csv(src_path)
        df_proc = proc_fn(df_raw)
        
        dest_path = os.path.join(DEST_DIR, file_name)
        df_proc.to_csv(dest_path, index=False)
        print(f"Saved normalized dataset to: {dest_path}\n")
        
    print("Text Normalization Completed Successfully!")

if __name__ == "__main__":
    main()
