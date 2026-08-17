from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_connection
from app.schemas.analytics_schemas import (
    ApplicationSummaryResponse,
    DropoffReasonCount,
    DropoffReasonsResponse,
    FunnelResponse,
    FunnelStageCount,
    JourneyEventResponse,
    JourneyListResponse,
    SummaryListResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/journey", response_model=JourneyListResponse)
async def get_journey(
    department: Optional[str] = Query(None, description="Filter by department"),
    application_id: Optional[str] = Query(None, description="Filter by specific application"),
    stage: Optional[str] = Query(None, description="Filter by stage name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    offset = (page - 1) * page_size
    where_clauses = []
    params = []

    if department:
        where_clauses.append("department = %s")
        params.append(department)

    if application_id:
        where_clauses.append("application_id = %s")
        params.append(application_id)

    if stage:
        where_clauses.append("stage_name = %s")
        params.append(stage)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) FROM core.v_application_journey {where_sql}",
                params,
            )
            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT
                    application_id, candidate_external_id, email, first_name, last_name,
                    job_id, job_title, department, stage_name, stage_order,
                    entered_at, exited_at, duration_days, stage_outcome,
                    dropoff_flag, dropoff_reason, is_current_stage, is_dropoff_stage, is_derived
                FROM core.v_application_journey
                {where_sql}
                ORDER BY application_id, stage_sequence
                LIMIT %s OFFSET %s
                """,
                params + [page_size, offset],
            )
            rows = cur.fetchall()

    data = [
        JourneyEventResponse(
            application_id=row[0],
            candidate_external_id=row[1],
            email=row[2],
            first_name=row[3],
            last_name=row[4],
            job_id=row[5],
            job_title=row[6],
            department=row[7],
            stage_name=row[8],
            stage_order=row[9],
            entered_at=row[10],
            exited_at=row[11],
            duration_days=float(row[12]) if row[12] is not None else None,
            stage_outcome=row[13],
            dropoff_flag=row[14],
            dropoff_reason=row[15],
            is_current_stage=row[16],
            is_dropoff_stage=row[17],
            is_derived=row[18],
        )
        for row in rows
    ]

    return JourneyListResponse(total=total, page=page, page_size=page_size, data=data)


@router.get("/summary", response_model=SummaryListResponse)
async def get_summary(
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by application_status"),
    date_from: Optional[date] = Query(None, description="Filter applications from this date"),
    date_to: Optional[date] = Query(None, description="Filter applications up to this date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    offset = (page - 1) * page_size
    where_clauses = []
    params = []

    if department:
        where_clauses.append("department = %s")
        params.append(department)

    if status:
        where_clauses.append("application_status = %s")
        params.append(status)

    if date_from:
        where_clauses.append("application_date >= %s")
        params.append(date_from)

    if date_to:
        where_clauses.append("application_date <= %s")
        params.append(date_to)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) FROM core.v_application_summary {where_sql}",
                params,
            )
            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT
                    application_id, candidate_external_id, email, job_id, job_title, department,
                    application_date, source, first_entered_at, last_event_at,
                    total_stages_entered, has_dropoff, dropoff_stage, dropoff_reason,
                    final_outcome, final_stage, is_hired, reached_offer_stage,
                    total_days_in_process, application_status
                FROM core.v_application_summary
                {where_sql}
                ORDER BY application_date DESC, application_id
                LIMIT %s OFFSET %s
                """,
                params + [page_size, offset],
            )
            rows = cur.fetchall()

    data = [
        ApplicationSummaryResponse(
            application_id=row[0],
            candidate_external_id=row[1],
            email=row[2],
            job_id=row[3],
            job_title=row[4],
            department=row[5],
            application_date=row[6],
            source=row[7],
            first_entered_at=row[8],
            last_event_at=row[9],
            total_stages_entered=row[10],
            has_dropoff=row[11],
            dropoff_stage=row[12],
            dropoff_reason=row[13],
            final_outcome=row[14],
            final_stage=row[15],
            is_hired=row[16],
            reached_offer_stage=row[17],
            total_days_in_process=float(row[18]) if row[18] is not None else None,
            application_status=row[19],
        )
        for row in rows
    ]

    return SummaryListResponse(total=total, page=page, page_size=page_size, data=data)


@router.get("/funnel", response_model=FunnelResponse)
async def get_funnel(
    department: Optional[str] = Query(None, description="Filter by department"),
):
    where_clause = ""
    params = []
    if department:
        where_clause = "WHERE department = %s"
        params.append(department)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                WITH stage_counts AS (
                    SELECT
                        department,
                        stage_name,
                        stage_order,
                        COUNT(DISTINCT application_id) AS applications_entered,
                        COUNT(DISTINCT CASE WHEN dropoff_flag = TRUE THEN application_id END) AS applications_dropped
                    FROM core.v_application_journey
                    {where_clause}
                    GROUP BY department, stage_name, stage_order
                )
                SELECT
                    stage_name,
                    stage_order,
                    applications_entered,
                    applications_dropped,
                    applications_entered - applications_dropped AS applications_advanced
                FROM stage_counts
                ORDER BY stage_order
                """,
                params,
            )
            rows = cur.fetchall()

    stages = []
    for row in rows:
        entered = row[2] or 0
        dropped = row[3] or 0
        advanced = row[4] or 0
        dropoff_rate = round((dropped / entered * 100) if entered else 0.0, 2)
        stages.append(
            FunnelStageCount(
                stage_name=row[0],
                stage_order=row[1],
                applications_entered=entered,
                applications_advanced=advanced,
                applications_dropped=dropped,
                dropoff_rate=dropoff_rate,
            )
        )

    return FunnelResponse(department=department, date_range=None, stages=stages)


@router.get("/dropoff-reasons", response_model=DropoffReasonsResponse)
async def get_dropoff_reasons(
    department: Optional[str] = Query(None, description="Filter by department"),
    stage: Optional[str] = Query(None, description="Filter by specific stage"),
):
    where_clauses = ["has_dropoff = TRUE"]
    params = []

    if department:
        where_clauses.append("department = %s")
        params.append(department)

    if stage:
        where_clauses.append("dropoff_stage = %s")
        params.append(stage)

    where_sql = "WHERE " + " AND ".join(where_clauses)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    COALESCE(dropoff_reason, 'Unknown') AS reason,
                    COUNT(*) AS count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
                FROM core.v_application_summary
                {where_sql}
                GROUP BY COALESCE(dropoff_reason, 'Unknown')
                ORDER BY count DESC, reason
                """,
                params,
            )
            rows = cur.fetchall()

    total_dropoffs = sum(row[1] for row in rows)
    reasons = [
        DropoffReasonCount(reason=row[0], count=row[1], percentage=float(row[2]) if row[2] is not None else 0.0)
        for row in rows
    ]

    return DropoffReasonsResponse(department=department, total_dropoffs=total_dropoffs, reasons=reasons)

