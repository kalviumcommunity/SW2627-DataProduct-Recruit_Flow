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


def _normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().lower()


def _prefetch_lookup_cache(cur) -> Dict[str, Dict[Any, Any]]:
    cache: Dict[str, Dict[Any, Any]] = {
        "candidate_by_id": {},
        "candidate_by_email": {},
        "candidate_by_phone": {},
        "job_by_id": {},
        "job_by_title_dept": {},
        "application_by_id": {},
        "application_details_by_id": {},
        "offer_by_id": {},
        "stage_by_name": {},
        "department_by_name": {},
    }

    cur.execute("SELECT id, name FROM core.departments")
    for dept_id, name in cur.fetchall():
        cache["department_by_name"][_normalize_text(name)] = dept_id

    cur.execute("SELECT id, name FROM core.stages")
    for stage_id, name in cur.fetchall():
        cache["stage_by_name"][_normalize_text(name)] = stage_id

    cur.execute("SELECT id, candidate_id, email, phone FROM core.candidates")
    for candidate_row in cur.fetchall():
        candidate_db_id, candidate_id, email, phone = candidate_row
        if candidate_id:
            cache["candidate_by_id"][candidate_id] = candidate_db_id
        if email:
            cache["candidate_by_email"][_normalize_text(email)] = candidate_db_id
        if phone:
            cache["candidate_by_phone"][_normalize_text(phone)] = candidate_db_id

    cur.execute("SELECT id, job_id, job_title, department_id FROM core.jobs")
    for job_db_id, job_id, job_title, department_id in cur.fetchall():
        if job_id:
            cache["job_by_id"][job_id] = job_db_id
        if job_title and department_id:
            cache["job_by_title_dept"][(_normalize_text(job_title), department_id)] = job_db_id

    cur.execute("SELECT id, application_id, candidate_id FROM core.applications")
    for app_db_id, application_id, candidate_id in cur.fetchall():
        if application_id:
            cache["application_by_id"][application_id] = app_db_id
            cache["application_details_by_id"][application_id] = (app_db_id, candidate_id)

    cur.execute("SELECT id, offer_id FROM core.offers")
    for offer_db_id, offer_id in cur.fetchall():
        if offer_id:
            cache["offer_by_id"][offer_id] = offer_db_id

    return cache


def _get_department_id(cur, department_name: str, lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None) -> Optional[int]:
    normalized = _normalize_text(department_name)
    if lookup_cache and normalized in lookup_cache["department_by_name"]:
        return lookup_cache["department_by_name"][normalized]

    cur.execute(
        """
        SELECT id
        FROM core.departments
        WHERE name = %s
        """,
        (department_name,),
    )
    result = cur.fetchone()
    if result and lookup_cache and normalized:
        lookup_cache["department_by_name"][normalized] = result[0]
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


def resolve_candidate(
    cur,
    staging_candidate: Dict[str, Any],
    batch_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Tuple[int, str, bool]:
    """
    Resolves a staging candidate to a core candidate ID.
    Returns: (core_candidate_id, match_type)
    """
    candidate_id = staging_candidate.get("candidate_id")
    email = staging_candidate.get("email")
    phone = staging_candidate.get("phone")

    if candidate_id:
        if lookup_cache and candidate_id in lookup_cache["candidate_by_id"]:
            return lookup_cache["candidate_by_id"][candidate_id], "existing_id", False
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
            if lookup_cache:
                lookup_cache["candidate_by_id"][candidate_id] = result[0]
            return result[0], "existing_id", False

    if email:
        normalized_email = _normalize_text(email)
        if lookup_cache and normalized_email in lookup_cache["candidate_by_email"]:
            result_id = lookup_cache["candidate_by_email"][normalized_email]
            if candidate_id:
                cur.execute(
                    """
                    UPDATE core.candidates
                    SET candidate_id = %s
                    WHERE id = %s
                    """,
                    (candidate_id, result_id),
                )
                lookup_cache["candidate_by_id"][candidate_id] = result_id
            return result_id, "email_match", False
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
                if lookup_cache:
                    lookup_cache["candidate_by_id"][candidate_id] = result[0]
            if lookup_cache and normalized_email:
                lookup_cache["candidate_by_email"][normalized_email] = result[0]
            return result[0], "email_match", False

    if phone:
        normalized_phone = _normalize_text(phone)
        if lookup_cache and normalized_phone in lookup_cache["candidate_by_phone"]:
            result_id = lookup_cache["candidate_by_phone"][normalized_phone]
            if candidate_id:
                cur.execute(
                    """
                    UPDATE core.candidates
                    SET candidate_id = %s
                    WHERE id = %s
                    """,
                    (candidate_id, result_id),
                )
                lookup_cache["candidate_by_id"][candidate_id] = result_id
            return result_id, "phone_match", False
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
                if lookup_cache:
                    lookup_cache["candidate_by_id"][candidate_id] = result[0]
            if lookup_cache and normalized_phone:
                lookup_cache["candidate_by_phone"][normalized_phone] = result[0]
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
    if lookup_cache:
        if candidate_id:
            lookup_cache["candidate_by_id"][candidate_id] = new_id
        if email:
            lookup_cache["candidate_by_email"][_normalize_text(email)] = new_id
        if phone:
            lookup_cache["candidate_by_phone"][_normalize_text(phone)] = new_id

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


def resolve_job(
    cur,
    staging_job: Dict[str, Any],
    department_id: int,
    batch_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Tuple[int, str]:
    job_id = staging_job.get("job_id")
    job_title = staging_job.get("job_title")

    if job_id:
        if lookup_cache and job_id in lookup_cache["job_by_id"]:
            return lookup_cache["job_by_id"][job_id], "existing_id"
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
            if lookup_cache:
                lookup_cache["job_by_id"][job_id] = result[0]
            return result[0], "existing_id"

    if job_title and department_id:
        normalized_title = _normalize_text(job_title)
        if lookup_cache and (normalized_title, department_id) in lookup_cache["job_by_title_dept"]:
            result_id = lookup_cache["job_by_title_dept"][(normalized_title, department_id)]
            if job_id:
                cur.execute(
                    """
                    UPDATE core.jobs
                    SET job_id = %s
                    WHERE id = %s
                    """,
                    (job_id, result_id),
                )
                lookup_cache["job_by_id"][job_id] = result_id
            return result_id, "title_dept_match"
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
                if lookup_cache:
                    lookup_cache["job_by_id"][job_id] = result[0]
            if lookup_cache:
                lookup_cache["job_by_title_dept"][(normalized_title, department_id)] = result[0]
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
    new_id = cur.fetchone()[0]
    if lookup_cache:
        if job_id:
            lookup_cache["job_by_id"][job_id] = new_id
        if job_title:
            lookup_cache["job_by_title_dept"][(_normalize_text(job_title), department_id)] = new_id
    return new_id, "created_new"


def resolve_application(
    cur,
    application_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Optional[int]:
    if lookup_cache and application_id in lookup_cache["application_by_id"]:
        return lookup_cache["application_by_id"][application_id]
    cur.execute(
        """
        SELECT id
        FROM core.applications
        WHERE application_id = %s
        """,
        (application_id,),
    )
    result = cur.fetchone()
    if result and lookup_cache:
        lookup_cache["application_by_id"][application_id] = result[0]
    return result[0] if result else None


def resolve_application_details(
    cur,
    application_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Tuple[Optional[int], Optional[int]]:
    if lookup_cache and application_id in lookup_cache["application_details_by_id"]:
        return lookup_cache["application_details_by_id"][application_id]
    cur.execute(
        """
        SELECT id, candidate_id
        FROM core.applications
        WHERE application_id = %s
        """,
        (application_id,),
    )
    result = cur.fetchone()
    if not result:
        return None, None
    if lookup_cache:
        lookup_cache["application_details_by_id"][application_id] = (result[0], result[1])
    return result[0], result[1]


def resolve_core_candidate_id(
    cur,
    candidate_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Optional[int]:
    if lookup_cache and candidate_id in lookup_cache["candidate_by_id"]:
        return lookup_cache["candidate_by_id"][candidate_id]
    cur.execute(
        """
        SELECT id
        FROM core.candidates
        WHERE candidate_id = %s
        """,
        (candidate_id,),
    )
    result = cur.fetchone()
    if result and lookup_cache:
        lookup_cache["candidate_by_id"][candidate_id] = result[0]
    return result[0] if result else None


def resolve_core_offer_id(
    cur,
    offer_id: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Optional[int]:
    if lookup_cache and offer_id in lookup_cache["offer_by_id"]:
        return lookup_cache["offer_by_id"][offer_id]
    cur.execute(
        """
        SELECT id
        FROM core.offers
        WHERE offer_id = %s
        """,
        (offer_id,),
    )
    result = cur.fetchone()
    if result and lookup_cache:
        lookup_cache["offer_by_id"][offer_id] = result[0]
    return result[0] if result else None


def _resolve_application_and_candidate(
    cur,
    row: Dict[str, Any],
    batch_id: str,
    entity_type: str,
    lookup_cache: Optional[Dict[str, Dict[Any, Any]]] = None,
) -> Tuple[Optional[int], Optional[int]]:
    application_external_id = row.get("application_id")
    candidate_external_id = row.get("candidate_id")

    app_internal_id, app_candidate_id = resolve_application_details(cur, application_external_id, lookup_cache)
    if not app_internal_id:
        _record_load_error(
            cur,
            batch_id,
            entity_type,
            row.get("source_row_number"),
            row.get(f"{entity_type[:-1]}_id") if row.get(f"{entity_type[:-1]}_id") else application_external_id,
            f"Application '{application_external_id}' not found in core.applications",
            row,
        )
        return None, None

    candidate_core_id = None
    if candidate_external_id:
        candidate_core_id = resolve_core_candidate_id(cur, candidate_external_id, lookup_cache)

    if candidate_core_id and app_candidate_id and candidate_core_id != app_candidate_id:
        _record_load_error(
            cur,
            batch_id,
            entity_type,
            row.get("source_row_number"),
            row.get(f"{entity_type[:-1]}_id") if row.get(f"{entity_type[:-1]}_id") else application_external_id,
            f"Candidate '{candidate_external_id}' does not match application '{application_external_id}'",
            row,
        )
        return None, None

    if not candidate_core_id:
        candidate_core_id = app_candidate_id

    if not candidate_core_id:
        _record_load_error(
            cur,
            batch_id,
            entity_type,
            row.get("source_row_number"),
            row.get(f"{entity_type[:-1]}_id") if row.get(f"{entity_type[:-1]}_id") else application_external_id,
            f"Candidate for application '{application_external_id}' could not be resolved",
            row,
        )
        return None, None

    return app_internal_id, candidate_core_id


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
        "interviews_loaded": 0,
        "offers_loaded": 0,
        "onboarding_loaded": 0,
        "duplicates_skipped": 0,
        "possible_duplicates_flagged": 0,
        "load_errors_recorded": 0,
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            lookup_cache = _prefetch_lookup_cache(cur)

            cur.execute(
                """
                SELECT *
                FROM staging.candidates
                WHERE ingestion_batch_id = %s
                """,
                (batch_id,),
            )
            staging_candidate_rows = cur.fetchall()
            staging_candidate_cols = [desc[0] for desc in cur.description]
            staging_candidates_by_id = {
                row[staging_candidate_cols.index("candidate_id")]: dict(zip(staging_candidate_cols, row))
                for row in staging_candidate_rows
                if row[staging_candidate_cols.index("candidate_id")]
            }

            cur.execute(
                """
                SELECT *
                FROM staging.jobs
                WHERE ingestion_batch_id = %s
                """,
                (batch_id,),
            )
            staging_job_rows = cur.fetchall()
            staging_job_cols = [desc[0] for desc in cur.description]
            staging_jobs_by_id = {
                row[staging_job_cols.index("job_id")]: dict(zip(staging_job_cols, row))
                for row in staging_job_rows
                if row[staging_job_cols.index("job_id")]
            }

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
                _, _, flagged = resolve_candidate(cur, row, batch_id, lookup_cache)
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
                department_id = _get_department_id(cur, row.get("department"), lookup_cache)
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
                resolve_job(cur, row, department_id, batch_id, lookup_cache)
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
                if resolve_application(cur, application_id, lookup_cache):
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

                staging_candidate = staging_candidates_by_id.get(row.get("candidate_id"))
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

                core_candidate_id, _, flagged = resolve_candidate(cur, staging_candidate, batch_id, lookup_cache)
                if flagged:
                    counts["possible_duplicates_flagged"] += 1

                staging_job = staging_jobs_by_id.get(row.get("job_id"))
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

                department_id = _get_department_id(cur, staging_job.get("department"), lookup_cache)
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

                core_job_id, _ = resolve_job(cur, staging_job, department_id, batch_id, lookup_cache)

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
                app_db_id = resolve_application(cur, application_id, lookup_cache)
                lookup_cache["application_details_by_id"][application_id] = (app_db_id, core_candidate_id)
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

                app_result = resolve_application(cur, row.get("application_id"), lookup_cache)
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

                stage_result = lookup_cache["stage_by_name"].get(_normalize_text(row.get("stage_name")))
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
                        app_result,
                        stage_result,
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

            # Interviews
            cur.execute(
                """
                SELECT *
                FROM staging.interviews
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            interview_rows = cur.fetchall()
            interview_cols = [desc[0] for desc in cur.description]

            for record in interview_rows:
                row = dict(zip(interview_cols, record))
                interview_id = row.get("interview_id")
                if not interview_id:
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.interviews
                    WHERE interview_id = %s
                    """,
                    (interview_id,),
                )
                if cur.fetchone():
                    counts["duplicates_skipped"] += 1
                    _record_load_error(
                        cur,
                        batch_id,
                        "interviews",
                        row.get("source_row_number"),
                        interview_id,
                        "Duplicate interview_id already exists in core.interviews",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                app_id, candidate_id = _resolve_application_and_candidate(cur, row, batch_id, "interviews", lookup_cache)
                if not app_id or not candidate_id:
                    counts["load_errors_recorded"] += 1
                    continue

                cur.execute(
                    """
                    INSERT INTO core.interviews
                    (interview_id, application_id, candidate_id, interview_type, scheduled_at, completed_at,
                     interview_status, technical_score, communication_score, overall_score, recommendation,
                     feedback, ingestion_batch_id, source_row_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        interview_id,
                        app_id,
                        candidate_id,
                        row.get("interview_type"),
                        row.get("scheduled_at"),
                        row.get("completed_at"),
                        row.get("interview_status"),
                        row.get("technical_score"),
                        row.get("communication_score"),
                        row.get("overall_score"),
                        row.get("recommendation"),
                        row.get("feedback"),
                        batch_id,
                        row.get("source_row_number"),
                    ),
                )
                counts["interviews_loaded"] += 1

            # Offers
            cur.execute(
                """
                SELECT *
                FROM staging.offers
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            offer_rows = cur.fetchall()
            offer_cols = [desc[0] for desc in cur.description]

            for record in offer_rows:
                row = dict(zip(offer_cols, record))
                offer_id = row.get("offer_id")
                if not offer_id:
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.offers
                    WHERE offer_id = %s
                    """,
                    (offer_id,),
                )
                if cur.fetchone():
                    counts["duplicates_skipped"] += 1
                    _record_load_error(
                        cur,
                        batch_id,
                        "offers",
                        row.get("source_row_number"),
                        offer_id,
                        "Duplicate offer_id already exists in core.offers",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                app_id, candidate_id = _resolve_application_and_candidate(cur, row, batch_id, "offers", lookup_cache)
                if not app_id or not candidate_id:
                    counts["load_errors_recorded"] += 1
                    continue

                cur.execute(
                    """
                    INSERT INTO core.offers
                    (offer_id, application_id, candidate_id, offer_date, offered_role, offered_salary,
                     currency, joining_date, offer_status, response_date, offer_rejection_reason,
                     ingestion_batch_id, source_row_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        offer_id,
                        app_id,
                        candidate_id,
                        row.get("offer_date"),
                        row.get("offered_role"),
                        row.get("offered_salary"),
                        row.get("currency"),
                        row.get("joining_date"),
                        row.get("offer_status"),
                        row.get("response_date"),
                        row.get("offer_rejection_reason"),
                        batch_id,
                        row.get("source_row_number"),
                    ),
                )
                counts["offers_loaded"] += 1

            # Onboarding
            cur.execute(
                """
                SELECT *
                FROM staging.onboarding
                WHERE ingestion_batch_id = %s
                  AND cleaned_status IN ('cleaned', 'review')
                ORDER BY source_row_number, staging_record_id
                """,
                (batch_id,),
            )
            onboarding_rows = cur.fetchall()
            onboarding_cols = [desc[0] for desc in cur.description]

            for record in onboarding_rows:
                row = dict(zip(onboarding_cols, record))
                onboarding_id = row.get("onboarding_id")
                if not onboarding_id:
                    continue

                cur.execute(
                    """
                    SELECT id
                    FROM core.onboarding
                    WHERE onboarding_id = %s
                    """,
                    (onboarding_id,),
                )
                if cur.fetchone():
                    counts["duplicates_skipped"] += 1
                    _record_load_error(
                        cur,
                        batch_id,
                        "onboarding",
                        row.get("source_row_number"),
                        onboarding_id,
                        "Duplicate onboarding_id already exists in core.onboarding",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                app_id, candidate_id = _resolve_application_and_candidate(cur, row, batch_id, "onboarding", lookup_cache)
                if not app_id or not candidate_id:
                    counts["load_errors_recorded"] += 1
                    continue

                offer_core_id = resolve_core_offer_id(cur, row.get("offer_id"), lookup_cache)
                if not offer_core_id:
                    _record_load_error(
                        cur,
                        batch_id,
                        "onboarding",
                        row.get("source_row_number"),
                        onboarding_id,
                        f"Offer '{row.get('offer_id')}' not found in core.offers",
                        row,
                    )
                    counts["load_errors_recorded"] += 1
                    continue

                cur.execute(
                    """
                    INSERT INTO core.onboarding
                    (onboarding_id, offer_id, application_id, candidate_id, planned_joining_date,
                     actual_joining_date, joining_status, no_join_reason, onboarding_completed,
                     ingestion_batch_id, source_row_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        onboarding_id,
                        offer_core_id,
                        app_id,
                        candidate_id,
                        row.get("planned_joining_date"),
                        row.get("actual_joining_date"),
                        row.get("joining_status"),
                        row.get("no_join_reason"),
                        row.get("onboarding_completed"),
                        batch_id,
                        row.get("source_row_number"),
                    ),
                )
                counts["onboarding_loaded"] += 1

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
    print(f"  - Interviews: {counts['interviews_loaded']}")
    print(f"  - Offers: {counts['offers_loaded']}")
    print(f"  - Onboarding: {counts['onboarding_loaded']}")
    print(f"  - Duplicates skipped: {counts['duplicates_skipped']}")
    print(f"  - Possible duplicates flagged: {counts['possible_duplicates_flagged']}")
    print(f"  - Load errors recorded: {counts['load_errors_recorded']}")

    return counts
