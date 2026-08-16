# backend/app/services/ingestion/deduplicator.py
import json
from typing import Dict, Any, Optional, Tuple

from app.core.database import get_connection


def _json_safe(value: Any) -> Any:
    """Recursively convert values into JSON-serializable shapes."""
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


def _email_domain(email: Optional[str]) -> Optional[str]:
    if not email or "@" not in email:
        return None
    return email.strip().lower().split("@", 1)[1]


def _get_department_id(cur, department_name: str) -> Optional[int]:
    cur.execute(
        """
        SELECT id
        FROM core.departments
        WHERE name = %s
        """,
        (department_name,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def _record_possible_duplicate(
    cur,
    batch_id: str,
    primary_record_id: int,
    secondary_record_id: int,
    matched_on: str,
    reason: str,
):
    cur.execute(
        """
        INSERT INTO core.possible_duplicates
        (ingestion_batch_id, entity_type, matched_on, primary_record_id, secondary_record_id, reason)
        VALUES (%s, 'candidate', %s, %s, %s, %s)
        """,
        (batch_id, matched_on, primary_record_id, secondary_record_id, reason),
    )
    return True


def _record_load_error(
    cur,
    batch_id: str,
    entity_type: str,
    source_row_number: Optional[int],
    external_id: Optional[str],
    reason: str,
    raw_data: Optional[Dict[str, Any]] = None,
):
    cur.execute(
        """
        INSERT INTO core.load_errors
        (ingestion_batch_id, entity_type, source_row_number, external_id, reason, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """,
        (
            batch_id,
            entity_type,
            source_row_number,
            external_id,
            reason,
            json.dumps(_json_safe(raw_data), default=str) if raw_data is not None else None,
        ),
    )


def resolve_candidate(cur, staging_candidate: Dict[str, Any], batch_id: str) -> Tuple[int, str, bool]:
    """
    Resolves a staging candidate to a core candidate ID.
    Returns: (core_candidate_id, match_type)
    """
    candidate_id = staging_candidate.get("candidate_id")
    email = staging_candidate.get("email")
    phone = staging_candidate.get("phone")

    if candidate_id:
        cur.execute(
            """
            SELECT id
            FROM core.candidates
            WHERE candidate_id = %s
            """,
            (candidate_id,),
        )
        result = cur.fetchone()
        if result:
            return result[0], "existing_id", False

    if email:
        cur.execute(
            """
            SELECT id
            FROM core.candidates
            WHERE LOWER(TRIM(email)) = LOWER(TRIM(%s))
              AND email IS NOT NULL
            ORDER BY id
            LIMIT 1
            """,
            (email,),
        )
        result = cur.fetchone()
        if result:
            if candidate_id:
                cur.execute(
                    """
                    UPDATE core.candidates
                    SET candidate_id = %s
                    WHERE id = %s
                    """,
                    (candidate_id, result[0]),
                )
            return result[0], "email_match", False

    if phone:
        cur.execute(
            """
            SELECT id
            FROM core.candidates
            WHERE TRIM(phone) = TRIM(%s)
              AND phone IS NOT NULL
            ORDER BY id
            LIMIT 1
            """,
            (phone,),
        )
        result = cur.fetchone()
        if result:
            if candidate_id:
                cur.execute(
                    """
                    UPDATE core.candidates
                    SET candidate_id = %s
                    WHERE id = %s
                    """,
                    (candidate_id, result[0]),
                )
            return result[0], "phone_match", False

    cur.execute(
        """
        INSERT INTO core.candidates
        (candidate_id, email, original_email, first_name, last_name, phone, ingestion_batch_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            candidate_id,
            email,
            staging_candidate.get("original_email"),
            staging_candidate.get("first_name"),
            staging_candidate.get("last_name"),
            phone,
            batch_id,
        ),
    )
    new_id = cur.fetchone()[0]

    first_name = (staging_candidate.get("first_name") or "").strip().lower()
    last_name = (staging_candidate.get("last_name") or "").strip().lower()
    domain = _email_domain(email)

    if first_name and last_name and domain:
        cur.execute(
            """
            SELECT id
            FROM core.candidates
            WHERE LOWER(TRIM(first_name)) = %s
              AND LOWER(TRIM(last_name)) = %s
              AND email IS NOT NULL
              AND SPLIT_PART(LOWER(TRIM(email)), '@', 2) = %s
              AND id <> %s
            ORDER BY id
            LIMIT 1
            """,
            (first_name, last_name, domain, new_id),
        )
        possible = cur.fetchone()
        if possible:
            _record_possible_duplicate(
                cur,
                batch_id,
                possible[0],
                new_id,
                "name+email_domain",
                "Same first/last name and email domain; manual review recommended.",
            )
            return new_id, "created_new", True

    return new_id, "created_new", False


def resolve_job(cur, staging_job: Dict[str, Any], department_id: int, batch_id: str) -> Tuple[int, str]:
    job_id = staging_job.get("job_id")
    job_title = staging_job.get("job_title")

    if job_id:
        cur.execute(
            """
            SELECT id
            FROM core.jobs
            WHERE job_id = %s
            """,
            (job_id,),
        )
        result = cur.fetchone()
        if result:
            return result[0], "existing_id"

    if job_title and department_id:
        cur.execute(
            """
            SELECT id
            FROM core.jobs
            WHERE job_title = %s
              AND department_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (job_title, department_id),
        )
        result = cur.fetchone()
        if result:
            if job_id:
                cur.execute(
                    """
                    UPDATE core.jobs
                    SET job_id = %s
                    WHERE id = %s
                    """,
                    (job_id, result[0]),
                )
            return result[0], "title_dept_match"

    cur.execute(
        """
        INSERT INTO core.jobs
        (job_id, job_title, department_id, location, employment_type, opening_date, closing_date, job_status, ingestion_batch_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            job_id,
            job_title,
            department_id,
            staging_job.get("location"),
            staging_job.get("employment_type"),
            staging_job.get("opening_date"),
            staging_job.get("closing_date"),
            staging_job.get("job_status"),
            batch_id,
        ),
    )
    return cur.fetchone()[0], "created_new"


def resolve_application(cur, application_id: str) -> Optional[int]:
    cur.execute(
        """
        SELECT id
        FROM core.applications
        WHERE application_id = %s
        """,
        (application_id,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def _fetch_staging_row_by_external_id(cur, table_name: str, id_column: str, external_id: str) -> Optional[Dict[str, Any]]:
    cur.execute(
        f"""
        SELECT *
        FROM {table_name}
        WHERE {id_column} = %s
        ORDER BY staging_record_id DESC
        LIMIT 1
        """,
        (external_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    columns = [desc[0] for desc in cur.description]
    return dict(zip(columns, row))


def deduplicate_batch(batch_id: str) -> Dict[str, int]:
    """
    Resolves cleaned staging records into core entities.
    """
    counts = {
        "candidates_loaded": 0,
        "jobs_loaded": 0,
        "applications_loaded": 0,
        "stage_events_loaded": 0,
        "duplicates_skipped": 0,
        "possible_duplicates_flagged": 0,
        "load_errors_recorded": 0,
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Candidates
            cur.execute(
                """
                SELECT *
                FROM staging.candidates
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            candidate_rows = cur.fetchall()
            candidate_cols = [desc[0] for desc in cur.description]

            for record in candidate_rows:
                row = dict(zip(candidate_cols, record))
                _, _, flagged = resolve_candidate(cur, row, batch_id)
                if flagged:
                    counts["possible_duplicates_flagged"] += 1
                counts["candidates_loaded"] += 1

            # Jobs
            cur.execute(
                """
                SELECT *
                FROM staging.jobs
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            job_rows = cur.fetchall()
            job_cols = [desc[0] for desc in cur.description]

            for record in job_rows:
                row = dict(zip(job_cols, record))
                department_id = _get_department_id(cur, row.get("department"))
                if not department_id:
                    print(f"Warning: Department '{row.get('department')}' not found in core.departments. Skipping job {row.get('job_id')}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "jobs",
                        row.get("source_row_number"),
                        row.get("job_id"),
                        f"Department '{row.get('department')}' not found in core.departments",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue
                resolve_job(cur, row, department_id, batch_id)
                counts["jobs_loaded"] += 1

            # Applications
            cur.execute(
                """
                SELECT *
                FROM staging.applications
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            app_rows = cur.fetchall()
            app_cols = [desc[0] for desc in cur.description]

            for record in app_rows:
                row = dict(zip(app_cols, record))
                application_id = row.get("application_id")
                if resolve_application(cur, application_id):
                    counts["duplicates_skipped"] += 1
                    _record_load_error(
                        cur,
                        batch_id,
                        "applications",
                        row.get("source_row_number"),
                        application_id,
                        "Duplicate application_id already exists in core.applications",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                staging_candidate = _fetch_staging_row_by_external_id(cur, "staging.candidates", "candidate_id", row.get("candidate_id"))
                if not staging_candidate:
                    print(f"Warning: Candidate '{row.get('candidate_id')}' not found in staging. Skipping application {application_id}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "applications",
                        row.get("source_row_number"),
                        application_id,
                        f"Candidate '{row.get('candidate_id')}' not found in staging or core",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                core_candidate_id, _, flagged = resolve_candidate(cur, staging_candidate, batch_id)
                if flagged:
                    counts["possible_duplicates_flagged"] += 1

                staging_job = _fetch_staging_row_by_external_id(cur, "staging.jobs", "job_id", row.get("job_id"))
                if not staging_job:
                    print(f"Warning: Job '{row.get('job_id')}' not found in staging. Skipping application {application_id}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "applications",
                        row.get("source_row_number"),
                        application_id,
                        f"Job '{row.get('job_id')}' not found in staging or core",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                department_id = _get_department_id(cur, staging_job.get("department"))
                if not department_id:
                    print(f"Warning: Department '{staging_job.get('department')}' not found in core.departments. Skipping application {application_id}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "applications",
                        row.get("source_row_number"),
                        application_id,
                        f"Department '{staging_job.get('department')}' not found in core.departments",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                core_job_id, _ = resolve_job(cur, staging_job, department_id, batch_id)

                cur.execute(
                    """
                    INSERT INTO core.applications
                    (application_id, candidate_id, job_id, application_date, source, ingestion_batch_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        application_id,
                        core_candidate_id,
                        core_job_id,
                        row.get("application_date"),
                        row.get("source"),
                        batch_id,
                    ),
                )
                counts["applications_loaded"] += 1

            # Stage events
            cur.execute(
                """
                SELECT *
                FROM staging.stage_events
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            stage_rows = cur.fetchall()
            stage_cols = [desc[0] for desc in cur.description]

            for record in stage_rows:
                row = dict(zip(stage_cols, record))
                stage_event_id = row.get("stage_event_id")
                if not stage_event_id:
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.stage_events
                    WHERE stage_event_id = %s
                    """,
                    (stage_event_id,),
                )
                if cur.fetchone():
                    counts["duplicates_skipped"] += 1
                    _record_load_error(
                        cur,
                        batch_id,
                        "stage_events",
                        row.get("source_row_number"),
                        stage_event_id,
                        "Duplicate stage_event_id already exists in core.stage_events",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.applications
                    WHERE application_id = %s
                    """,
                    (row.get("application_id"),),
                )
                app_result = cur.fetchone()
                if not app_result:
                    print(f"Warning: Application '{row.get('application_id')}' not found in core. Skipping stage event {stage_event_id}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "stage_events",
                        row.get("source_row_number"),
                        stage_event_id,
                        f"Application '{row.get('application_id')}' not found in core.applications",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.stages
                    WHERE name = %s
                    """,
                    (row.get("stage_name"),),
                )
                stage_result = cur.fetchone()
                if not stage_result:
                    print(f"Warning: Stage '{row.get('stage_name')}' not found in core.stages. Skipping stage event {stage_event_id}")
                    _record_load_error(
                        cur,
                        batch_id,
                        "stage_events",
                        row.get("source_row_number"),
                        stage_event_id,
                        f"Stage '{row.get('stage_name')}' not found in core.stages",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                dropoff_flag = row.get("dropoff_flag")
                if isinstance(dropoff_flag, str):
                    dropoff_flag = dropoff_flag.lower() in {"true", "1", "yes", "t", "y"}

                cur.execute(
                    """
                    INSERT INTO core.stage_events
                    (stage_event_id, application_id, stage_id, entered_at, exited_at,
                     dropoff_flag, dropoff_reason, feedback, ingestion_batch_id, source_row_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        stage_event_id,
                        app_result[0],
                        stage_result[0],
                        row.get("entered_at"),
                        row.get("exited_at"),
                        dropoff_flag,
                        row.get("dropoff_reason"),
                        row.get("feedback"),
                        batch_id,
                        row.get("source_row_number"),
                    ),
                )
                counts["stage_events_loaded"] += 1

            cur.execute(
                """
                UPDATE core.ingestion_batches
                SET status = 'core_loaded',
                    duplicate_rows = %s
                WHERE id = %s
                """,
                (counts["duplicates_skipped"], batch_id),
            )
            conn.commit()

    print(f"Deduplication complete for batch {batch_id}")
    print(f"  - Candidates: {counts['candidates_loaded']}")
    print(f"  - Jobs: {counts['jobs_loaded']}")
    print(f"  - Applications: {counts['applications_loaded']}")
    print(f"  - Stage Events: {counts['stage_events_loaded']}")
    print(f"  - Duplicates skipped: {counts['duplicates_skipped']}")
    print(f"  - Possible duplicates flagged: {counts['possible_duplicates_flagged']}")
    print(f"  - Load errors recorded: {counts['load_errors_recorded']}")

    return counts
