import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from backend.db.connection import get_connection

# Data science pipeline runners
from src.cleaning.clean_data import main as run_cleaning
from src.cleaning.deduplicate_data import main as run_deduplication
from src.cleaning.normalize_text import main as run_text_norm
from src.validation.validate_data import validate_datasets as run_validation
from src.transformation.build_candidate_journey import build_journeys as run_journey_builder
from src.transformation.feature_engineering import engineer_features as run_feature_engineering
from src.analysis.funnel import calculate_funnel as run_funnel_calculator
from src.analysis.department import calculate_department_analytics as run_department_analysis
from src.analysis.role import calculate_role_analytics as run_role_analysis
from src.analysis.reasons import calculate_reasons as run_reasons_analysis
from src.analysis.dropoff import calculate_dropoff as run_dropoff_analysis
from src.analysis.stage_duration import calculate_stage_durations as run_stage_duration_analysis
from src.analysis.intelligence import generate_hr_intelligence as run_intelligence_analysis

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
BATCHES_JSON_PATH = os.path.join(PROCESSED_DIR, "batches_store.json")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def _load_fallback_batches() -> List[Dict[str, Any]]:
    if os.path.exists(BATCHES_JSON_PATH):
        try:
            with open(BATCHES_JSON_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_fallback_batches(batches: List[Dict[str, Any]]):
    with open(BATCHES_JSON_PATH, "w") as f:
        json.dump(batches, f, indent=2)

def list_batches(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all active or recorded ingestion batches."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                if status_filter:
                    cur.execute("""
                        SELECT id, batch_name, status, total_records, accepted_records, rejected_records, created_at, updated_at
                        FROM core.ingestion_batches
                        WHERE status = %s
                        ORDER BY created_at DESC
                    """, (status_filter,))
                else:
                    cur.execute("""
                        SELECT id, batch_name, status, total_records, accepted_records, rejected_records, created_at, updated_at
                        FROM core.ingestion_batches
                        ORDER BY created_at DESC
                    """)
                rows = cur.fetchall()
                batches = []
                for r in rows:
                    batches.append({
                        "id": str(r[0]),
                        "batch_name": r[1],
                        "status": r[2],
                        "total_records": r[3] or 0,
                        "accepted_records": r[4] or 0,
                        "rejected_records": r[5] or 0,
                        "created_at": r[6].isoformat() if r[6] else None,
                        "updated_at": r[7].isoformat() if r[7] else None
                    })
                return batches
        except Exception as e:
            print(f"Error querying batches from PostgreSQL: {e}")
        finally:
            conn.close()
            
    # Fallback store
    batches = _load_fallback_batches()
    if status_filter:
        return [b for b in batches if b.get("status") == status_filter]
    return batches

def get_batch_by_id(batch_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single batch by ID."""
    batches = list_batches()
    for b in batches:
        if str(b["id"]) == str(batch_id):
            return b
    return None

def create_batch(batch_name: str, user_id: Optional[Any] = None) -> Dict[str, Any]:
    """Creates a new ingestion batch."""
    batch_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.ingestion_batches (id, user_id, batch_name, status, total_records, accepted_records, rejected_records, created_at, updated_at)
                    VALUES (%s, %s, %s, 'active', 0, 0, 0, NOW(), NOW())
                """, (batch_id, user_id, batch_name))
                conn.commit()
        except Exception as e:
            print(f"Error creating batch in PostgreSQL: {e}")
        finally:
            conn.close()
            
    # Save to fallback
    batches = _load_fallback_batches()
    new_batch = {
        "id": batch_id,
        "batch_name": batch_name,
        "status": "active",
        "user_id": user_id,
        "total_records": 0,
        "accepted_records": 0,
        "rejected_records": 0,
        "created_at": now_iso,
        "updated_at": now_iso
    }
    batches.insert(0, new_batch)
    _save_fallback_batches(batches)
    return new_batch

def append_to_batch(batch_id: str, new_records_count: int = 0) -> Dict[str, Any]:
    """Appends records to an existing active batch and triggers the analytical pipeline."""
    batch = get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch ID '{batch_id}' not found.")
    if batch.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Batch '{batch_id}' is {batch.get('status')} and cannot receive new data.")
        
    updated_total = (batch.get("total_records") or 0) + new_records_count
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE core.ingestion_batches
                    SET total_records = %s, updated_at = NOW()
                    WHERE id = %s
                """, (updated_total, batch_id))
                conn.commit()
        except Exception as e:
            print(f"Error updating batch in PostgreSQL: {e}")
        finally:
            conn.close()
            
    batches = _load_fallback_batches()
    for b in batches:
        if str(b["id"]) == str(batch_id):
            b["total_records"] = updated_total
            b["updated_at"] = now_iso
    _save_fallback_batches(batches)
    
    # Re-run full data science analytics pipeline
    try:
        run_cleaning()
        run_deduplication()
        run_text_norm()
        run_validation()
        run_journey_builder()
        run_feature_engineering()
        run_funnel_calculator()
        run_department_analysis()
        run_role_analysis()
        run_reasons_analysis()
        run_dropoff_analysis()
        run_stage_duration_analysis()
        run_intelligence_analysis()
    except Exception as e:
        print(f"Pipeline execution during batch append finished with note: {e}")
        
    return {
        "status": "success",
        "message": f"Successfully appended data to batch '{batch_id}' and refreshed analytics pipeline.",
        "batch_id": batch_id,
        "total_records": updated_total
    }

def delete_batch(batch_id: str) -> Dict[str, Any]:
    """Clears a batch, purges its database records, and resets analytics."""
    batch = get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch ID '{batch_id}' not found.")
        
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Cascade delete rows associated with this batch
                cur.execute("DELETE FROM core.candidates WHERE ingestion_batch_id = %s", (batch_id,))
                cur.execute("DELETE FROM core.recruitment_stages WHERE ingestion_batch_id = %s", (batch_id,))
                cur.execute("DELETE FROM core.interviews WHERE ingestion_batch_id = %s", (batch_id,))
                cur.execute("DELETE FROM core.onboarding WHERE ingestion_batch_id = %s", (batch_id,))
                cur.execute("DELETE FROM core.ingestion_batches WHERE id = %s", (batch_id,))
                conn.commit()
        except Exception as e:
            print(f"Error purging batch in PostgreSQL: {e}")
        finally:
            conn.close()
            
    batches = _load_fallback_batches()
    batches = [b for b in batches if str(b["id"]) != str(batch_id)]
    _save_fallback_batches(batches)
    
    return {
        "status": "success",
        "message": f"Batch '{batch_id}' successfully cleared and purged from system.",
        "batch_id": batch_id
    }
