import os
import uuid
import pandas as pd
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.db.connection import get_connection

# Import Data Science Engine modules
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

router = APIRouter(prefix="/upload", tags=["Upload"])

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

@router.post("/file/{entity_type}")
async def upload_entity_file(entity_type: str, file: UploadFile = File(...)):
    """
    Uploads a raw CSV file (candidates, recruitment_stages, interviews, onboarding),
    saves it to data/raw/, and inserts metadata into PostgreSQL core.ingestion_batches & core tables.
    """
    if entity_type not in ["candidates", "recruitment_stages", "interviews", "onboarding"]:
        raise HTTPException(status_code=400, detail="Invalid entity type. Must be candidates, recruitment_stages, interviews, or onboarding.")
        
    batch_id = str(uuid.uuid4())
    file_path = os.path.join(RAW_DATA_DIR, f"{entity_type}.csv")
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            
        df = pd.read_csv(file_path)
        row_count = len(df)
        
        # Save metadata to PostgreSQL if database connection is live
        conn = get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.ingestion_batches (id, batch_name, status, total_records)
                    VALUES (%s, %s, 'active', %s)
                    ON CONFLICT (id) DO NOTHING
                """, (batch_id, f"Upload_{entity_type}_{file.filename}", row_count))
                conn.commit()
            conn.close()
            
        return {
            "status": "success",
            "message": f"Successfully uploaded {file.filename} containing {row_count} rows.",
            "batch_id": batch_id,
            "entity_type": entity_type,
            "saved_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@router.post("/process-pipeline")
async def trigger_full_pipeline():
    """
    Triggers the complete Data Science Engine pipeline over data/raw files:
    Cleaning -> Deduplication -> Normalization -> Validation -> Journey Building -> Feature Engineering -> Funnel Calculation.
    """
    try:
        print("Trigering full Data Science Pipeline...")
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
        
        return {
            "status": "success",
            "message": "Data Science pipeline executed successfully. Funnel metrics updated!",
            "processed_dir": "data/processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
