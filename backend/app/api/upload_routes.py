# backend/app/api/upload_routes.py
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from app.core.database import get_connection
from app.schemas.ingestion_schemas import (
    BatchStatusResponse,
    BatchSummaryResponse,
    UploadResponse,
    ValidationErrorListResponse,
    ValidationErrorResponse,
)
from app.services.ingestion.file_handler import (
    save_uploaded_file, create_ingestion_batch, update_batch_status, calculate_file_hash
)
from app.services.ingestion.parser import parse_file_to_raw_records, store_raw_records
from app.services.ingestion.staging_service import process_batch_to_staging
from app.services.ingestion.cleaner import clean_batch
from app.services.ingestion.deduplicator import deduplicate_batch
from app.services.ingestion.journey_builder import derive_missing_applied_stage, ensure_chronological_ordering
from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["Ingestion"])

@router.post("/", response_model=UploadResponse)
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

        # 10. Reconstruct candidate journeys
        derived_stages = derive_missing_applied_stage(batch_id)
        ensure_chronological_ordering(batch_id)

        update_batch_status(batch_id, "journey_reconstructed")

        # 11. Return ingestion result
        return {
            "batch_id": batch_id,
            "status": "journey_reconstructed",
            "total_rows": sum(len(rows) for rows in parsed_data.values()),
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "cleaned_rows": cleaned_rows,
            "core_loaded": core_loaded,
            "derived_stages": derived_stages,
            "entities_found": list(parsed_data.keys())
        }
    
    except Exception as e:
        update_batch_status(batch_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    filename,
                    file_hash,
                    status,
                    total_rows,
                    accepted_rows,
                    rejected_rows,
                    duplicate_rows,
                    uploaded_at,
                    error_message
                FROM core.ingestion_batches
                WHERE id = %s
                """,
                (str(batch_id),),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Batch not found")

            cur.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT 1 FROM staging.candidates WHERE ingestion_batch_id = %s AND validation_status = 'warning'
                    UNION ALL
                    SELECT 1 FROM staging.jobs WHERE ingestion_batch_id = %s AND validation_status = 'warning'
                    UNION ALL
                    SELECT 1 FROM staging.applications WHERE ingestion_batch_id = %s AND validation_status = 'warning'
                    UNION ALL
                    SELECT 1 FROM staging.stage_events WHERE ingestion_batch_id = %s AND validation_status = 'warning'
                ) warnings
                """,
                (str(batch_id), str(batch_id), str(batch_id), str(batch_id)),
            )
            warning_rows = cur.fetchone()[0]

    uploaded_at = row[8]
    processing_duration_ms = None
    if uploaded_at:
        processing_duration_ms = int((datetime.now(timezone.utc) - uploaded_at).total_seconds() * 1000)

    return BatchStatusResponse(
        id=row[0],
        filename=row[1],
        file_hash=row[2],
        status=row[3],
        total_rows=row[4],
        accepted_rows=row[5],
        rejected_rows=row[6],
        warning_rows=warning_rows or 0,
        duplicate_rows=row[7] or 0,
        uploaded_at=uploaded_at,
        processing_duration_ms=processing_duration_ms,
        error_message=row[9],
    )


@router.get("/{batch_id}/errors", response_model=ValidationErrorListResponse)
async def get_batch_errors(
    batch_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM core.validation_errors
                WHERE ingestion_batch_id = %s
                """,
                (str(batch_id),),
            )
            total = cur.fetchone()[0]

            cur.execute(
                """
                SELECT id, entity_type, source_row_number, error_message, raw_data, created_at
                FROM core.validation_errors
                WHERE ingestion_batch_id = %s
                ORDER BY source_row_number NULLS LAST, id
                LIMIT %s OFFSET %s
                """,
                (str(batch_id), limit, offset),
            )
            rows = cur.fetchall()

    errors = [
        ValidationErrorResponse(
            id=row[0],
            entity_type=row[1],
            source_row_number=row[2],
            error_message=row[3],
            raw_data=row[4],
            created_at=row[5],
        )
        for row in rows
    ]

    return ValidationErrorListResponse(batch_id=batch_id, total_errors=total, errors=errors)


@router.get("/{batch_id}/summary", response_model=BatchSummaryResponse)
async def get_batch_summary(batch_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, status, total_rows, accepted_rows, rejected_rows
                FROM core.ingestion_batches
                WHERE id = %s
                """,
                (str(batch_id),),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Batch not found")

            cur.execute(
                """
                SELECT 'candidates' AS entity, COUNT(*) FROM staging.candidates WHERE ingestion_batch_id = %s
                UNION ALL
                SELECT 'jobs', COUNT(*) FROM staging.jobs WHERE ingestion_batch_id = %s
                UNION ALL
                SELECT 'applications', COUNT(*) FROM staging.applications WHERE ingestion_batch_id = %s
                UNION ALL
                SELECT 'stage_events', COUNT(*) FROM staging.stage_events WHERE ingestion_batch_id = %s
                """,
                (str(batch_id), str(batch_id), str(batch_id), str(batch_id)),
            )
            entity_rows = cur.fetchall()
            entities = {entity: count for entity, count in entity_rows}

    return BatchSummaryResponse(
        batch_id=batch_id,
        filename=row[0],
        status=row[1],
        totals={"total": row[2], "accepted": row[3], "rejected": row[4]},
        entities=entities,
    )
