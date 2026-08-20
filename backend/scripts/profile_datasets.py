import os
import pandas as pd
import glob
import json

MOCK_DIR = r"c:\Users\eemai\OneDrive\Desktop\WBD\SPRJCT\RecruitFlow\backend\uploads\mockdatasets"

def profile_dataset(file_path):
    filename = os.path.basename(file_path)
    df = pd.read_csv(file_path)
    
    print(f"="*60)
    print(f" DATA PROFILING REPORT: {filename}")
    print(f"="*60)
    
    # 1. Shape
    rows, cols = df.shape
    print(f"\n1. SHAPE:")
    print(f"   - Rows: {rows}")
    print(f"   - Columns: {cols}")
    
    # 2. Columns & Data Types
    print(f"\n2. COLUMNS & DATA TYPES:")
    for col, dtype in df.dtypes.items():
        print(f"   - {col:<25}: {dtype}")
        
    # 3. Missing Values
    print(f"\n3. MISSING VALUES:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        pct = (count / rows) * 100
        print(f"   - {col:<25}: {count} ({pct:.1f}%)")
        
    # 4. Duplicates
    print(f"\n4. DUPLICATES:")
    total_dups = df.duplicated().sum()
    print(f"   - Full Row Duplicates: {total_dups}")
    
    id_cols = [c for c in df.columns if 'id' in c.lower()]
    for id_col in id_cols:
        dup_ids = df[id_col].duplicated().sum()
        print(f"   - Duplicate Key '{id_col}': {dup_ids}")
        
    # 5. Unique Values / Value Counts
    print(f"\n5. UNIQUE VALUES & CATEGORICAL DISTRIBUTIONS:")
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        n_unique = len(unique_vals)
        print(f"\n   Column: '{col}' (Unique count: {n_unique})")
        if n_unique <= 15:
            val_counts = df[col].value_counts(dropna=False).to_dict()
            print(f"     Values: {val_counts}")
        else:
            sample_vals = list(unique_vals[:5])
            print(f"     Sample values (first 5): {sample_vals}")

def main():
    csv_files = glob.glob(os.path.join(MOCK_DIR, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in {MOCK_DIR}")
        return
        
    for f in sorted(csv_files):
        profile_dataset(f)
        print("\n\n")

if __name__ == "__main__":
    main()
