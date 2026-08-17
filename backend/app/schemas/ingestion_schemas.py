from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    batch_id: UUID
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    cleaned_rows: Optional[Dict[str, int]] = None
    core_loaded: Optional[Dict[str, int]] = None
    derived_stages: Optional[int] = None
    entities_found: List[str]
    message: Optional[str] = None


class BatchStatusResponse(BaseModel):
    id: UUID
    filename: str
    file_hash: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    warning_rows: int
    duplicate_rows: int
    uploaded_at: datetime
    processing_duration_ms: Optional[int] = None
    error_message: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    id: int
    entity_type: str
    source_row_number: Optional[int]
    error_message: str
    raw_data: Optional[Dict]
    created_at: datetime


class ValidationErrorListResponse(BaseModel):
    batch_id: UUID
    total_errors: int
    errors: List[ValidationErrorResponse]


class BatchSummaryResponse(BaseModel):
    batch_id: UUID
    filename: str
    status: str
    totals: Dict[str, int]
    entities: Dict[str, int]

