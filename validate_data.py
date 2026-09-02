import pandas as pd
import sys

def validate(path):
    df = pd.read_csv(path)
    errors = []

    # Required columns
    required = ["customer_id", "order_id", "amount", "date", "segment"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append("Missing columns: " + str(missing))
    else:
        print("PASS: Required columns present")

    # Data types
    if "amount" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["amount"]):
            errors.append("amount column is not numeric")
        else:
            print("PASS: amount is numeric")

    # Minimum rows
    if len(df) < 100:
        errors.append("Row count " + str(len(df)) + " below minimum 100")
    else:
        print("PASS: Row count " + str(len(df)) + " meets minimum")

    # Null columns
    null_cols = [c for c in df.columns if df[c].isnull().all()]
    if null_cols:
        errors.append("Fully null columns: " + str(null_cols))
    else:
        print("PASS: No fully null columns")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  ERROR: " + e)
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")

if __name__ == "__main__":
    validate(sys.argv[1])
