from datetime import date, datetime, time

from app.core.database import get_connection


def _application_date_to_timestamptz(application_date):
    if application_date is None:
        return None
    if isinstance(application_date, datetime):
        return application_date
    if isinstance(application_date, date):
        return datetime.combine(application_date, time.min)
    return application_date


def _get_affected_applications(cur, batch_id: str):
    cur.execute(
        """
        SELECT DISTINCT a.id, a.application_id, a.application_date
        FROM core.applications a
        LEFT JOIN core.stage_events se ON se.application_id = a.id
        WHERE a.ingestion_batch_id = %s
           OR se.ingestion_batch_id = %s
        ORDER BY a.id
        """,
        (batch_id, batch_id),
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
