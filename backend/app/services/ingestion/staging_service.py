# backend/app/services/ingestion/staging_service.py
import json
from typing import Dict, List
from app.core.database import get_connection
from app.services.ingestion.validator import validate_record

def process_batch_to_staging(batch_id: str):
    """
    Reads all raw records for a batch, validates them, and inserts valid records
    into staging tables. Invalid records go to core.validation_errors.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Fetch all raw records for this batch
            cur.execute("""
                SELECT id, entity_type, source_row_number, raw_data
                FROM raw.raw_records
                WHERE ingestion_batch_id = %s
                ORDER BY entity_type, source_row_number
            """, (batch_id,))
            raw_records = cur.fetchall()
            
            accepted_count = 0
            rejected_count = 0
            
            for raw_id, entity_type, row_num, raw_json in raw_records:
                # psycopg2 can return jsonb as a dict, so support both shapes.
                row_data = raw_json if isinstance(raw_json, dict) else json.loads(raw_json)
                
                # 2. Validate the record
                result = validate_record(row_data, entity_type, row_num)
                
                if result["valid"]:
                    # 3. Insert into appropriate staging table
                    validation_status = "warning" if result["warnings"] else "valid"
                    insert_staging_record(
                        conn,
                        entity_type,
                        batch_id,
                        raw_id,
                        row_num,
                        result["cleaned_data"],
                        validation_status
                    )
                    accepted_count += 1
                else:
                    # 4. Insert into validation_errors
                    insert_validation_error(conn, batch_id, entity_type, row_num, result["errors"], raw_json)
                    rejected_count += 1
            
            # 5. Update the batch status
            cur.execute("""
                UPDATE core.ingestion_batches 
                SET accepted_rows = %s, rejected_rows = %s, status = 'validated'
                WHERE id = %s
            """, (accepted_count, rejected_count, batch_id))
            conn.commit()
    
    print(f"Validation complete for batch {batch_id}: {accepted_count} accepted, {rejected_count} rejected")
    return accepted_count, rejected_count

def insert_staging_record(
    conn,
    entity_type: str,
    batch_id: str,
    raw_id: int,
    row_num: int,
    data: Dict,
    validation_status: str,
):
    """Inserts a validated record into the appropriate staging table."""
    with conn.cursor() as cur:
        if entity_type == "candidates":
            cur.execute("""
                INSERT INTO staging.candidates 
                (ingestion_batch_id, raw_record_id, source_row_number, validation_status, validation_error_count,
                 candidate_id, email, original_email, first_name, last_name, phone)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, %s, %s)
            """, (
                batch_id, raw_id, row_num, validation_status,
                data.get("candidate_id"), data.get("email"), data.get("original_email"),
                data.get("first_name"), data.get("last_name"), data.get("phone")
            ))
        
        elif entity_type == "jobs":
            cur.execute("""
                INSERT INTO staging.jobs 
                (ingestion_batch_id, raw_record_id, source_row_number, validation_status, validation_error_count,
                 job_id, job_title, department, location, employment_type)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, %s)
            """, (
                batch_id, raw_id, row_num, validation_status,
                data.get("job_id"), data.get("job_title"), data.get("department"),
                data.get("location"), data.get("employment_type")
            ))
        
        elif entity_type == "applications":
            cur.execute("""
                INSERT INTO staging.applications 
                (ingestion_batch_id, raw_record_id, source_row_number, validation_status, validation_error_count,
                 application_id, candidate_id, job_id, application_date, source)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, %s)
            """, (
                batch_id, raw_id, row_num, validation_status,
                data.get("application_id"), data.get("candidate_id"), data.get("job_id"),
                data.get("application_date"), data.get("source")
            ))
        
        elif entity_type == "stage_events":
            cur.execute("""
                INSERT INTO staging.stage_events 
                (ingestion_batch_id, raw_record_id, source_row_number, validation_status, validation_error_count,
                 stage_event_id, application_id, stage_name, entered_at, exited_at, 
                 stage_outcome, dropoff_flag, dropoff_reason)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                batch_id, raw_id, row_num, validation_status,
                data.get("stage_event_id"), data.get("application_id"), data.get("stage_name"),
                data.get("entered_at"), data.get("exited_at"), data.get("stage_outcome"),
                data.get("dropoff_flag", False), data.get("dropoff_reason")
            ))
        # Add other entity types similarly...

def insert_validation_error(conn, batch_id: str, entity_type: str, row_num: int, errors: List[str], raw_json: str):
    """Inserts a validation error record."""
    with conn.cursor() as cur:
        error_message = "; ".join(errors)
        raw_payload = json.dumps(raw_json) if isinstance(raw_json, dict) else raw_json
        cur.execute("""
            INSERT INTO core.validation_errors 
            (ingestion_batch_id, entity_type, source_row_number, error_message, raw_data)
            VALUES (%s, %s, %s, %s, %s::jsonb)
        """, (batch_id, entity_type, row_num, error_message, raw_payload))
