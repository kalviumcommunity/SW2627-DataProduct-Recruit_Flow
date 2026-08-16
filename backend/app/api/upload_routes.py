# backend/app/api/upload_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.ingestion.file_handler import (
    save_uploaded_file, create_ingestion_batch, update_batch_status, calculate_file_hash
)
from app.services.ingestion.parser import parse_file_to_raw_records, store_raw_records
from app.services.ingestion.staging_service import process_batch_to_staging
from app.services.ingestion.cleaner import clean_batch
from app.services.ingestion.deduplicator import deduplicate_batch
from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["Ingestion"])

@router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,  # We will use this in Phase 10, but keep it for now
    file: UploadFile = File(...)
):
    """
    Accepts CSV or Excel file, stores it raw, and creates ingestion batch.
    """
    # 1. Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["csv", "xlsx", "xls"]:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported.")
    
    # 2. Read and save the file
    storage_path, file_hash, content = await save_uploaded_file(file)
    
    # 3. Check for idempotency (Duplicate file detection)
    # (We will implement this properly later, but for now we just create a new batch)
    
    # 4. Create ingestion batch
    batch_id = create_ingestion_batch(
        filename=file.filename,
        file_hash=file_hash,
        file_type=file_extension
    )
    
    try:
        # 5. Parse the file
        parsed_data = parse_file_to_raw_records(storage_path, file_extension)
        
        # 6. Store raw records in the database
        store_raw_records(batch_id, parsed_data, file.filename)

        # 7. Validate and move valid records to staging
        accepted, rejected = process_batch_to_staging(batch_id)

        # 8. Clean the validated records
        cleaned_rows = clean_batch(batch_id)

        # 9. Deduplicate and load into core
        core_loaded = deduplicate_batch(batch_id)

        # 10. Return ingestion result
        return {
            "batch_id": batch_id,
            "status": "core_loaded",
            "total_rows": sum(len(rows) for rows in parsed_data.values()),
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "cleaned_rows": cleaned_rows,
            "core_loaded": core_loaded,
            "entities_found": list(parsed_data.keys())
        }
    
    except Exception as e:
        update_batch_status(batch_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
