from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from backend.services.batch_service import (
    list_batches,
    create_batch,
    append_to_batch,
    delete_batch,
    get_batch_by_id
)

router = APIRouter(prefix="/batches", tags=["Batch Management"])

class CreateBatchRequest(BaseModel):
    batch_name: str = Field(..., min_length=1, description="Descriptive name for the recruitment data batch")

class AppendBatchRequest(BaseModel):
    new_records_count: Optional[int] = Field(0, description="Number of candidate records appended")

@router.get("", response_model=List[Dict[str, Any]])
async def get_batches(status: Optional[str] = None):
    """
    Lists present batches for HR (e.g. active, cleared, processing).
    """
    return list_batches(status_filter=status)

@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_new_batch(req: CreateBatchRequest):
    """
    Creates a new ingestion batch for recruitment data tracking.
    """
    if not req.batch_name or not req.batch_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch name cannot be empty."
        )
    new_batch = create_batch(batch_name=req.batch_name.strip())
    return {
        "status": "success",
        "message": f"Batch '{req.batch_name}' created successfully.",
        "batch": new_batch
    }

@router.post("/{batch_id}/append")
async def append_to_existing_batch(batch_id: str, req: Optional[AppendBatchRequest] = None):
    """
    Appends newly uploaded data to an existing active batch and triggers the analytical pipeline.
    """
    records_count = req.new_records_count if req else 0
    result = append_to_batch(batch_id=batch_id, new_records_count=records_count)
    return result

@router.delete("/{batch_id}")
async def clear_existing_batch(batch_id: str):
    """
    Clears a batch, purges its associated PostgreSQL database rows, and resets analytics.
    """
    result = delete_batch(batch_id=batch_id)
    return result
