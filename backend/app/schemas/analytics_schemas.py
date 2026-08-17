from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class JourneyEventResponse(BaseModel):
    application_id: str
    candidate_external_id: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    job_id: str
    job_title: str
    department: str
    stage_name: str
    stage_order: int
    entered_at: datetime
    exited_at: Optional[datetime]
    duration_days: Optional[float]
    stage_outcome: Optional[str]
    dropoff_flag: bool
    dropoff_reason: Optional[str]
    is_current_stage: bool
    is_dropoff_stage: bool
    is_derived: bool


class JourneyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[JourneyEventResponse]


class ApplicationSummaryResponse(BaseModel):
    application_id: str
    candidate_external_id: str
    email: Optional[str]
    job_id: str
    job_title: str
    department: str
    application_date: date
    source: Optional[str]
    first_entered_at: Optional[datetime]
    last_event_at: Optional[datetime]
    total_stages_entered: int
    has_dropoff: bool
    dropoff_stage: Optional[str]
    dropoff_reason: Optional[str]
    final_outcome: Optional[str]
    final_stage: Optional[str]
    is_hired: bool
    reached_offer_stage: bool
    total_days_in_process: Optional[float]
    application_status: str


class SummaryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[ApplicationSummaryResponse]


class FunnelStageCount(BaseModel):
    stage_name: str
    stage_order: int
    applications_entered: int
    applications_advanced: int
    applications_dropped: int
    dropoff_rate: float


class FunnelResponse(BaseModel):
    department: Optional[str]
    date_range: Optional[Dict[str, date]]
    stages: List[FunnelStageCount]


class DropoffReasonCount(BaseModel):
    reason: str
    count: int
    percentage: float


class DropoffReasonsResponse(BaseModel):
    department: Optional[str]
    total_dropoffs: int
    reasons: List[DropoffReasonCount]

