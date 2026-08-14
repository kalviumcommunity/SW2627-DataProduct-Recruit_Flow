# backend/app/services/ingestion/parser.py
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Any

# Allowed entity types (must match our file names)
ENTITY_TYPES = ["candidates", "jobs", "applications", "stage_events", "interviews", "offers", "onboarding"]

def parse_file_to_raw_records(file_path: str, file_type: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parses a CSV or Excel file and returns a dictionary of entity_type -> list of rows.
    For CSV: only one sheet/entity per file.
    For Excel: loops through sheets (each sheet corresponds to an entity type).
    """
    parsed_data = {}
    path = Path(file_path)
    
    if file_type == "csv":
        # CSV contains only one entity type. We infer the entity from the filename.
        entity_name = path.stem.split('_')[-1] if '_' in path.stem else path.stem
        if entity_name in ENTITY_TYPES:
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            # Convert NaN to None for JSON serialization
            parsed_data[entity_name] = df.replace({pd.NA: None, float('nan'): None}).to_dict(orient='records')
        else:
            raise ValueError(f"Unknown entity type inferred from filename: {entity_name}")
    
    elif file_type in ["xlsx", "xls"]:
        # Excel has multiple sheets. Each sheet name should match an entity type.
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            if sheet_name in ENTITY_TYPES:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str, keep_default_na=False)
                parsed_data[sheet_name] = df.replace({pd.NA: None, float('nan'): None}).to_dict(orient='records')
            else:
                # Skip unknown sheets, but log them
                print(f"Warning: Unknown sheet '{sheet_name}' ignored.")
    
    return parsed_data

def store_raw_records(batch_id: str, parsed_data: Dict[str, List[Dict]], source_filename: str):
    """Inserts parsed rows into raw.raw_records as JSONB."""
    from app.core.database import get_connection
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            for entity_type, rows in parsed_data.items():
                for idx, row in enumerate(rows, start=1):
                    # Convert row dict to JSON string
                    raw_json = json.dumps(row, default=str)  # default=str handles datetime objects
                    
                    cur.execute("""
                        INSERT INTO raw.raw_records 
                        (ingestion_batch_id, entity_type, source_file_name, source_row_number, raw_data)
                        VALUES (%s, %s, %s, %s, %s::jsonb)
                    """, (batch_id, entity_type, source_filename, idx, raw_json))
            
            # Update the total_rows count in ingestion_batches
            total_rows = sum(len(rows) for rows in parsed_data.values())
            cur.execute("""
                UPDATE core.ingestion_batches 
                SET total_rows = %s, status = 'staged' 
                WHERE id = %s
            """, (total_rows, batch_id))
            conn.commit()
    
    print(f"✅ Stored {total_rows} raw records for batch {batch_id}")