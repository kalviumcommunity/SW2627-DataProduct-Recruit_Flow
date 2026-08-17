from datetime import date, datetime, time
from typing import Optional

from app.core.database import get_connection


def _application_date_to_timestamptz(application_date):
    if application_date is None:
        return None
    if isinstance(application_date, datetime):
        return application_date
    if isinstance(application_date, date):
        return datetime.combine(application_date, time.min)
    return application_date


def _get_stage_id(cur, stage_name: str) -> Optional[int]:
    cur.execute(
        """
        SELECT id
        FROM core.stages
        WHERE name = %s
        """,
        (stage_name,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def _get_affected_applications(cur, batch_id: str):
    cur.execute(
        """
        SELECT DISTINCT a.id, a.application_id, a.application_date
        FROM core.applications a
        WHERE a.ingestion_batch_id = %s
           OR EXISTS (
                SELECT 1
                FROM core.stage_events se
                WHERE se.application_id = a.id
                  AND se.ingestion_batch_id = %s
           )
           OR EXISTS (
                SELECT 1
                FROM core.interviews i
                WHERE i.application_id = a.id
                  AND i.ingestion_batch_id = %s
           )
           OR EXISTS (
                SELECT 1
                FROM core.offers o
                WHERE o.application_id = a.id
                  AND o.ingestion_batch_id = %s
           )
           OR EXISTS (
                SELECT 1
                FROM core.onboarding ob
                WHERE ob.application_id = a.id
                  AND ob.ingestion_batch_id = %s
           )
        ORDER BY a.id
        """,
        (batch_id, batch_id, batch_id, batch_id, batch_id),
    )
    return cur.fetchall()


def derive_missing_applied_stage(batch_id: str) -> int:
    """
    Derive an Applied stage for applications in this batch that do not have one.
    """
    derived_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            missing_apps = [
                (app_id, application_code, application_date)
                for app_id, application_code, application_date in _get_affected_applications(cur, batch_id)
                if not _has_applied_stage(cur, app_id)
            ]

            if not missing_apps:
                return 0

            cur.execute(
                """
                SELECT id
                FROM core.stages
                WHERE name = 'Applied'
                """
            )
            stage_result = cur.fetchone()
            if not stage_result:
                print("Warning: 'Applied' stage not found in core.stages. Cannot derive journey rows.")
                return 0

            applied_stage_id = stage_result[0]

            for app_internal_id, app_id, app_date in missing_apps:
                entered_at = _application_date_to_timestamptz(app_date)
                cur.execute(
                    """
                    INSERT INTO core.stage_events
                    (stage_event_id, application_id, stage_id, entered_at, is_derived, derivation_reason, ingestion_batch_id)
                    VALUES (%s, %s, %s, %s, TRUE, %s, %s)
                    ON CONFLICT (stage_event_id) DO NOTHING
                    RETURNING id
                    """,
                    (
                        f"DERIVED-{app_id}-APPLIED",
                        app_internal_id,
                        applied_stage_id,
                        entered_at,
                        "Derived from application_date",
                        batch_id,
                    ),
                )
                if cur.fetchone():
                    derived_count += 1

            conn.commit()

    print(f"Derived {derived_count} missing 'Applied' stages for batch {batch_id}")
    return derived_count


def _insert_derived_stage_event(
    cur,
    stage_event_id: str,
    application_id: int,
    stage_name: str,
    entered_at,
    exited_at,
    stage_outcome: str,
    batch_id: str,
    derivation_reason: str,
    dropoff_flag: bool = False,
    dropoff_reason: Optional[str] = None,
    feedback: Optional[str] = None,
) -> bool:
    stage_id = _get_stage_id(cur, stage_name)
    if not stage_id:
        print(f"Warning: Stage '{stage_name}' not found in core.stages. Skipping {stage_event_id}")
        return False

    cur.execute(
        """
        INSERT INTO core.stage_events
        (stage_event_id, application_id, stage_id, entered_at, exited_at,
         stage_outcome, dropoff_flag, dropoff_reason, feedback,
         is_derived, derivation_reason, ingestion_batch_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
        ON CONFLICT (stage_event_id) DO NOTHING
        RETURNING id
        """,
        (
            stage_event_id,
            application_id,
            stage_id,
            entered_at,
            exited_at,
            stage_outcome,
            dropoff_flag,
            dropoff_reason,
            feedback,
            derivation_reason,
            batch_id,
        ),
    )
    return cur.fetchone() is not None


def _normalize_text(value) -> str:
    return (str(value).strip() if value is not None else "").strip()


def _infer_interview_stage_name(interview_type: Optional[str]) -> str:
    text = _normalize_text(interview_type).lower()
    if any(token in text for token in ("phone", "screen", "recruiter")):
        return "Recruiter Screen"
    if any(token in text for token in ("technical", "tech")):
        return "Technical Interview"
    if any(token in text for token in ("final", "cultural", "behaviour", "behavior", "panel", "onsite")):
        return "Final Interview"
    if any(token in text for token in ("manager", "hiring manager")):
        return "Hiring Manager Review"
    return "Technical Interview"


def _infer_interview_outcome(status: Optional[str], recommendation: Optional[str]) -> tuple[str, bool, Optional[str]]:
    status_text = _normalize_text(status)
    recommendation_text = _normalize_text(recommendation)
    status_lower = status_text.lower()
    recommendation_lower = recommendation_text.lower()

    if status_lower == "cancelled":
        return "Cancelled", True, "Interview cancelled"

    if recommendation_lower in {"strong hire", "hire"}:
        return "Passed", False, None

    if recommendation_lower in {"leaning no", "no hire"}:
        return "Failed", True, "Interview recommendation below threshold"

    if status_text:
        return status_text, False, None

    return "Completed", False, None


def _infer_offer_stage_name(offer_status: Optional[str]) -> str:
    if _normalize_text(offer_status).lower() == "accepted":
        return "Offer Accepted"
    return "Offer"


def _infer_offer_outcome(row) -> tuple[str, bool, Optional[str]]:
    status = _normalize_text(row.get("offer_status"))
    status_lower = status.lower()
    reason = _normalize_text(row.get("offer_rejection_reason")) or None

    if status_lower in {"declined", "expired"}:
        if not reason and status_lower == "expired":
            reason = "Offer expired"
        return status or "Declined", True, reason

    if status_lower == "accepted":
        return "Accepted", False, None

    return status or "Sent", False, None


def _infer_onboarding_outcome(row) -> tuple[str, bool, Optional[str]]:
    status = _normalize_text(row.get("joining_status"))
    status_lower = status.lower()
    completed = row.get("onboarding_completed")
    reason = _normalize_text(row.get("no_join_reason")) or None

    if status_lower == "joined" or completed is True or str(completed).lower() == "true":
        return "Joined", False, None

    if not reason:
        reason = status or "Onboarding not completed"

    return status or "Cancelled", True, reason


def derive_supporting_journey_events(batch_id: str) -> int:
    """
    Derive journey stage events from interviews, offers, and onboarding rows.
    """
    derived_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    i.id,
                    i.interview_id,
                    i.application_id,
                    i.interview_type,
                    i.scheduled_at,
                    i.completed_at,
                    i.interview_status,
                    i.recommendation,
                    i.feedback
                FROM core.interviews i
                WHERE i.ingestion_batch_id = %s
                ORDER BY i.application_id, i.scheduled_at, i.id
                """,
                (batch_id,),
            )
            interview_rows = cur.fetchall()
            for row in interview_rows:
                (
                    _id,
                    interview_id,
                    application_id,
                    interview_type,
                    scheduled_at,
                    completed_at,
                    interview_status,
                    recommendation,
                    feedback,
                ) = row
                stage_name = _infer_interview_stage_name(interview_type)
                stage_outcome, dropoff_flag, dropoff_reason = _infer_interview_outcome(interview_status, recommendation)
                entered_at = scheduled_at or completed_at
                exited_at = completed_at or scheduled_at
                if _insert_derived_stage_event(
                    cur,
                    f"DERIVED-INT-{interview_id}",
                    application_id,
                    stage_name,
                    entered_at,
                    exited_at,
                    stage_outcome,
                    batch_id,
                    "Derived from interview record",
                    dropoff_flag=dropoff_flag,
                    dropoff_reason=dropoff_reason,
                    feedback=feedback,
                ):
                    derived_count += 1

            cur.execute(
                """
                SELECT
                    o.id,
                    o.offer_id,
                    o.application_id,
                    o.offer_date,
                    o.offered_role,
                    o.offer_status,
                    o.response_date,
                    o.offer_rejection_reason,
                    o.joining_date
                FROM core.offers o
                WHERE o.ingestion_batch_id = %s
                ORDER BY o.application_id, o.offer_date, o.id
                """,
                (batch_id,),
            )
            offer_rows = cur.fetchall()
            for row in offer_rows:
                (
                    _id,
                    offer_id,
                    application_id,
                    offer_date,
                    offered_role,
                    offer_status,
                    response_date,
                    offer_rejection_reason,
                    joining_date,
                ) = row
                stage_name = _infer_offer_stage_name(offer_status)
                stage_outcome, dropoff_flag, dropoff_reason = _infer_offer_outcome(
                    {
                        "offer_status": offer_status,
                        "offer_rejection_reason": offer_rejection_reason,
                    }
                )
                entered_at = offer_date or response_date or joining_date
                exited_at = response_date or joining_date or offer_date
                if _insert_derived_stage_event(
                    cur,
                    f"DERIVED-OFF-{offer_id}",
                    application_id,
                    stage_name,
                    entered_at,
                    exited_at,
                    stage_outcome,
                    batch_id,
                    "Derived from offer record",
                    dropoff_flag=dropoff_flag,
                    dropoff_reason=dropoff_reason,
                    feedback=None,
                ):
                    derived_count += 1

            cur.execute(
                """
                SELECT
                    ob.id,
                    ob.onboarding_id,
                    ob.application_id,
                    ob.planned_joining_date,
                    ob.actual_joining_date,
                    ob.joining_status,
                    ob.no_join_reason,
                    ob.onboarding_completed
                FROM core.onboarding ob
                WHERE ob.ingestion_batch_id = %s
                ORDER BY ob.application_id, ob.planned_joining_date, ob.id
                """,
                (batch_id,),
            )
            onboarding_rows = cur.fetchall()
            for row in onboarding_rows:
                (
                    _id,
                    onboarding_id,
                    application_id,
                    planned_joining_date,
                    actual_joining_date,
                    joining_status,
                    no_join_reason,
                    onboarding_completed,
                ) = row
                stage_outcome, dropoff_flag, dropoff_reason = _infer_onboarding_outcome(
                    {
                        "joining_status": joining_status,
                        "no_join_reason": no_join_reason,
                        "onboarding_completed": onboarding_completed,
                    }
                )
                entered_at = planned_joining_date or actual_joining_date
                exited_at = actual_joining_date or planned_joining_date
                if _insert_derived_stage_event(
                    cur,
                    f"DERIVED-ONB-{onboarding_id}",
                    application_id,
                    "Joined",
                    entered_at,
                    exited_at,
                    stage_outcome,
                    batch_id,
                    "Derived from onboarding record",
                    dropoff_flag=dropoff_flag,
                    dropoff_reason=dropoff_reason,
                    feedback=None,
                ):
                    derived_count += 1

            conn.commit()

    print(f"Derived {derived_count} supporting journey events for batch {batch_id}")
    return derived_count


def _has_applied_stage(cur, application_id: int) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM core.stage_events se
        JOIN core.stages s ON se.stage_id = s.id
        WHERE se.application_id = %s
          AND s.name = 'Applied'
        LIMIT 1
        """,
        (application_id,),
    )
    return cur.fetchone() is not None


def ensure_chronological_ordering(batch_id: str) -> None:
    """
    Ensure exited_at values flow forward in time for each application.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    se.id,
                    se.application_id,
                    se.entered_at,
                    se.exited_at,
                    LEAD(se.entered_at) OVER (
                        PARTITION BY se.application_id
                        ORDER BY se.entered_at, se.id
                    ) AS next_entered_at
                FROM core.stage_events se
                JOIN core.applications a ON se.application_id = a.id
                WHERE a.ingestion_batch_id = %s
                   OR se.ingestion_batch_id = %s
                ORDER BY se.application_id, se.entered_at, se.id
                """,
                (batch_id, batch_id),
            )
            events = cur.fetchall()

            updates = 0
            for event_id, _, _, exited_at, next_entered_at in events:
                if exited_at is None and next_entered_at is not None:
                    cur.execute(
                        """
                        UPDATE core.stage_events
                        SET exited_at = %s
                        WHERE id = %s
                        """,
                        (next_entered_at, event_id),
                    )
                    updates += 1

            conn.commit()
            print(f"Fixed chronological ordering for {updates} stage events in batch {batch_id}")
