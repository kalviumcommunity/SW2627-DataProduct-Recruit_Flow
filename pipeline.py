import argparse
import logging
import os
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def ingest(path):
    logger.info("Ingesting: " + path)
    df = pd.read_csv(path)
    logger.info("Rows ingested: " + str(len(df)))
    return df

def clean(df):
    logger.info("Cleaning...")
    initial = len(df)
    df = df.dropna(subset=["customer_id", "amount"]).copy()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"] > 0]
    logger.info("Cleaned: " + str(initial) + " -> " + str(len(df)))
    return df

def aggregate(df):
    logger.info("Aggregating...")
    agg = df.groupby("segment").agg(
        revenue=("amount", "sum"),
        orders=("order_id", "count")
    ).reset_index()
    logger.info("Segments: " + str(len(agg)))
    return agg

def output(df, agg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(os.path.join(out_dir, "cleaned.csv"), index=False)
    agg.to_csv(os.path.join(out_dir, "aggregated.csv"), index=False)
    logger.info("Output written to: " + out_dir)
    logger.info("Pipeline complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest-clean-aggregate-output data pipeline")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", default="output", help="Output directory path")
    args = parser.parse_args()
    raw = ingest(args.input)
    cleaned = clean(raw)
    agg = aggregate(cleaned)
    output(cleaned, agg, args.output)
