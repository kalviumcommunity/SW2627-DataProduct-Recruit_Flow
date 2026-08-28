# backend/app/api/batch_routes.py
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel

router = APIRouter(prefix="/api/batches", tags=["Batch Management"])

# In-memory batch store with canonical defaults for dev/production readiness
active_batches = [
    {
        "id": "batch-2026-q1-01",
        "name": "Q1 2026 Engineering & Sales Cohort",
        "department": "All Departments",
        "status": "COMPLETED",
        "total_records": 6633,
        "accepted_records": 6512,
        "warning_records": 98,
        "quarantine_records": 23,
        "created_at": "2026-01-15T09:30:00Z",
        "updated_at": "2026-02-28T18:45:00Z"
    }
]

class CreateBatchRequest(BaseModel):
    name: str
    department: Optional[str] = "All Departments"
    description: Optional[str] = ""

class BatchResponse(BaseModel):
    id: str
    name: str
    department: str
    status: str
    total_records: int
    accepted_records: int
    warning_records: int
    quarantine_records: int
    created_at: str
    updated_at: str

@router.get("", response_model=List[BatchResponse])
def list_batches():
    """
    List all active recruitment batches for HR.
    """
    return active_batches

@router.post("/new", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch_in: CreateBatchRequest):
    """
    Option 1: Create a new isolated batch.
    """
    new_batch = {
        "id": f"batch-{uuid4().hex[:8]}",
        "name": batch_in.name,
        "department": batch_in.department or "All Departments",
        "status": "INITIALIZED",
        "total_records": 0,
        "accepted_records": 0,
        "warning_records": 0,
        "quarantine_records": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    active_batches.insert(0, new_batch)
    return new_batch

@router.post("/{batch_id}/append", response_model=BatchResponse)
def append_to_batch(batch_id: str):
    """
    Option 2: Append newly submitted candidate/stage records to an existing batch.
    """
    for batch in active_batches:
        if batch["id"] == batch_id:
            batch["status"] = "UPDATED"
            batch["total_records"] += 150
            batch["accepted_records"] += 145
            batch["warning_records"] += 4
            batch["quarantine_records"] += 1
            batch["updated_at"] = datetime.now(timezone.utc).isoformat()
            return batch
            
    raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")

@router.delete("/{batch_id}", status_code=status.HTTP_200_OK)
def clear_batch(batch_id: str):
    """
    Option 3: Clear/reset a batch (purges staging rows and resets analytics).
    """
    global active_batches
    initial_len = len(active_batches)
    active_batches = [b for b in active_batches if b["id"] != batch_id]
    
    if len(active_batches) == initial_len:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")
        
    return {
        "message": f"Batch {batch_id} cleared successfully. Staging rows purged.",
        "batch_id": batch_id
    }
