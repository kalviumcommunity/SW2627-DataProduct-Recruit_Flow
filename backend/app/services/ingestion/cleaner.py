# backend/app/services/ingestion/cleaner.py
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from app.core.database import get_connection

# ============================================================
# Canonical mappings
# ============================================================

DEPARTMENT_MAP = {
    "engineering": "Engineering",
    "eng": "Engineering",
    "engg": "Engineering",
    "it": "IT",
    "information technology": "IT",
    "information tech": "IT",
    "sales": "Sales",
    "marketing": "Marketing",
    "hr": "HR",
    "human resources": "HR",
    "finance": "Finance",
    "financial": "Finance",
}

STAGE_MAP = {
    "applied": "Applied",
    "application": "Applied",
    "screen": "Screening",
    "screening": "Screening",
    "recruiter screen": "Recruiter Screen",
    "recruiter": "Recruiter Screen",
    "hiring manager": "Hiring Manager Review",
    "hiring manager review": "Hiring Manager Review",
    "hm review": "Hiring Manager Review",
    "tech interview": "Technical Interview",
    "technical interview": "Technical Interview",
    "technical round": "Technical Interview",
    "tech round": "Technical Interview",
    "final interview": "Final Interview",
    "final round": "Final Interview",
    "hr interview": "Final Interview",
    "offer": "Offer",
    "offer released": "Offer",
    "offer accepted": "Offer Accepted",
    "accepted offer": "Offer Accepted",
    "joined": "Joined",
    "hire": "Joined",
}

DROPOFF_REASON_MAP = {
    "tech": "Technical Mismatch",
    "technical": "Technical Mismatch",
    "skill": "Technical Mismatch",
    "salary": "Salary Expectation",
    "pay": "Salary Expectation",
    "compensation": "Salary Expectation",
    "location": "Location Constraint",
    "relocate": "Location Constraint",
    "notice": "Notice Period",
    "withdrew": "Candidate Withdrew",
    "withdraw": "Candidate Withdrew",
    "no response": "No Response",
    "ghost": "No Response",
    "offer rejected": "Offer Rejected",
    "declined": "Offer Rejected",
    "position closed": "Position Closed",
    "closed": "Position Closed",
    "hiring freeze": "Position Closed",
    "other": "Other",
}

INTERVIEW_STATUS_MAP = {
    "scheduled": "Scheduled",
    "rescheduled": "Scheduled",
    "complete": "Completed",
    "completed": "Completed",
    "done": "Completed",
    "cancel": "Cancelled",
    "cancelled": "Cancelled",
    "canceled": "Cancelled",
}

INTERVIEW_RECOMMENDATION_MAP = {
    "strong hire": "Strong Hire",
    "hire": "Hire",
    "leaning no": "Leaning No",
    "no hire": "No Hire",
}

OFFER_STATUS_MAP = {
    "sent": "Sent",
    "offered": "Sent",
    "accepted": "Accepted",
    "offer accepted": "Accepted",
    "declined": "Declined",
    "rejected": "Declined",
    "expired": "Expired",
}

JOINING_STATUS_MAP = {
    "joined": "Joined",
    "hired": "Joined",
    "no show": "No Show",
    "noshow": "No Show",
    "postponed": "Postponed",
    "deferred": "Postponed",
    "cancelled": "Cancelled",
    "canceled": "Cancelled",
    "withdrawn": "Cancelled",
}


def clean_string(value: Any) -> Optional[str]:
    """Trim whitespace and collapse internal spacing."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    cleaned = re.sub(r"\s+", " ", value.strip())
    return cleaned if cleaned else None


def clean_email(value: Any) -> Optional[str]:
    cleaned = clean_string(value)
    return cleaned.lower() if cleaned else None


def normalize_department(value: Any) -> Tuple[Optional[str], bool, bool]:
    """
    Returns (canonical_value, standardized, needs_review).
    """
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    lower = cleaned.lower()
    if lower in DEPARTMENT_MAP:
        canonical = DEPARTMENT_MAP[lower]
        return canonical, canonical != cleaned, False

    if cleaned in DEPARTMENT_MAP.values():
        return cleaned, False, False

    return cleaned, False, True


def normalize_stage(value: Any) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    lower = cleaned.lower()
    if lower in STAGE_MAP:
        canonical = STAGE_MAP[lower]
        return canonical, canonical != cleaned, False

    if cleaned in STAGE_MAP.values():
        return cleaned, False, False

    return cleaned, False, True


def normalize_dropoff_reason(value: Any) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    lower = cleaned.lower()
    if lower in DROPOFF_REASON_MAP:
        canonical = DROPOFF_REASON_MAP[lower]
        return canonical, canonical != cleaned, False

    return cleaned, False, True


def normalize_vocabulary(value: Any, mapping: Dict[str, str]) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    lower = cleaned.lower()
    if lower in mapping:
        canonical = mapping[lower]
        return canonical, canonical != cleaned, False

    if cleaned in mapping.values():
        return cleaned, False, False

    return cleaned, False, True


def normalize_boolean_text(value: Any) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if cleaned is None:
        return "false", False, False

    lowered = cleaned.lower()
    if lowered in {"true", "1", "yes", "t", "y"}:
        return "true", lowered != "true", False
    if lowered in {"false", "0", "no", "f", "n"}:
        return "false", lowered != "false", False
    return lowered, False, True


def normalize_decimal_text(value: Any) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    stripped = cleaned.replace(",", "")
    if stripped.startswith("$"):
        stripped = stripped[1:]

    try:
        normalized = f"{float(stripped):.2f}"
        return normalized, normalized != cleaned, False
    except ValueError:
        return cleaned, False, True


def parse_date_to_iso(value: Any) -> Tuple[Optional[str], bool, bool]:
    """
    Returns (iso_date, parsed, needs_review).
    Ambiguous slash-formats are left untouched and flagged for review.
    """
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    direct_formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d-%b-%Y",
        "%d %b %Y",
    ]

    for fmt in direct_formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d"), True, False
        except ValueError:
            continue

    slash_match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", cleaned)
    if slash_match:
        part1 = int(slash_match.group(1))
        part2 = int(slash_match.group(2))
        year = int(slash_match.group(3))

        if part1 > 12 and part2 <= 12:
            dt = datetime(year, part2, part1)
            return dt.strftime("%Y-%m-%d"), True, False

        if part2 > 12 and part1 <= 12:
            dt = datetime(year, part1, part2)
            return dt.strftime("%Y-%m-%d"), True, False

        return cleaned, False, True

    return cleaned, False, True


def parse_timestamp_to_iso(value: Any) -> Tuple[Optional[str], bool, bool]:
    cleaned = clean_string(value)
    if not cleaned:
        return None, False, False

    direct_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]

    for fmt in direct_formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S"), True, False
        except ValueError:
            continue

    date_val, parsed, needs_review = parse_date_to_iso(cleaned)
    if parsed and date_val:
        return f"{date_val} 00:00:00", True, False

    return date_val, False, needs_review


def clean_candidate_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    original_email = clean_string(row.get("original_email")) or clean_string(row.get("email"))
    cleaned_email = clean_email(row.get("email"))

    cleaned["candidate_id"] = clean_string(row.get("candidate_id"))
    cleaned["email"] = cleaned_email
    cleaned["original_email"] = original_email
    cleaned["first_name"] = clean_string(row.get("first_name"))
    cleaned["last_name"] = clean_string(row.get("last_name"))
    cleaned["phone"] = clean_string(row.get("phone"))
    cleaned["_email_standardized"] = bool(
        original_email and cleaned_email and original_email.lower() != cleaned_email
    )

    return cleaned, "cleaned"


def clean_job_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["job_id"] = clean_string(row.get("job_id"))
    cleaned["job_title"] = clean_string(row.get("job_title"))
    cleaned["location"] = clean_string(row.get("location"))
    cleaned["employment_type"] = clean_string(row.get("employment_type"))

    department, standardized, review = normalize_department(row.get("department"))
    cleaned["department"] = department
    cleaned["_department_standardized"] = standardized
    needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_application_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["application_id"] = clean_string(row.get("application_id"))
    cleaned["candidate_id"] = clean_string(row.get("candidate_id"))
    cleaned["job_id"] = clean_string(row.get("job_id"))
    cleaned["source"] = clean_string(row.get("source"))

    date_val, parsed, review = parse_date_to_iso(row.get("application_date"))
    cleaned["application_date"] = date_val
    cleaned["_date_parsed"] = parsed
    needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_stage_event_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["stage_event_id"] = clean_string(row.get("stage_event_id"))
    cleaned["application_id"] = clean_string(row.get("application_id"))
    cleaned["stage_outcome"] = clean_string(row.get("stage_outcome"))

    stage, standardized, review = normalize_stage(row.get("stage_name"))
    cleaned["stage_name"] = stage
    cleaned["_stage_standardized"] = standardized
    needs_review = needs_review or review

    entered, entered_parsed, entered_review = parse_timestamp_to_iso(row.get("entered_at"))
    cleaned["entered_at"] = entered
    cleaned["_entered_parsed"] = entered_parsed
    needs_review = needs_review or entered_review

    exited, exited_parsed, exited_review = parse_timestamp_to_iso(row.get("exited_at"))
    cleaned["exited_at"] = exited
    cleaned["_exited_parsed"] = exited_parsed
    needs_review = needs_review or exited_review

    dropoff_raw = clean_string(row.get("dropoff_flag"))
    if dropoff_raw is None:
        cleaned["dropoff_flag"] = "false"
        cleaned["_dropoff_flag_standardized"] = False
    else:
        lowered = dropoff_raw.lower()
        if lowered in {"true", "1", "yes", "t", "y"}:
            cleaned["dropoff_flag"] = "true"
            cleaned["_dropoff_flag_standardized"] = lowered != "true"
        elif lowered in {"false", "0", "no", "f", "n"}:
            cleaned["dropoff_flag"] = "false"
            cleaned["_dropoff_flag_standardized"] = lowered != "false"
        else:
            cleaned["dropoff_flag"] = lowered
            cleaned["_dropoff_flag_standardized"] = False
            needs_review = True

    reason, standardized, review = normalize_dropoff_reason(row.get("dropoff_reason"))
    cleaned["dropoff_reason"] = reason
    cleaned["_reason_standardized"] = standardized
    needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_interview_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["interview_id"] = clean_string(row.get("interview_id"))
    cleaned["application_id"] = clean_string(row.get("application_id"))
    cleaned["candidate_id"] = clean_string(row.get("candidate_id"))
    cleaned["interview_type"] = clean_string(row.get("interview_type"))
    cleaned["feedback"] = clean_string(row.get("feedback"))

    scheduled, scheduled_parsed, scheduled_review = parse_timestamp_to_iso(row.get("scheduled_at"))
    cleaned["scheduled_at"] = scheduled
    cleaned["_scheduled_parsed"] = scheduled_parsed
    needs_review = needs_review or scheduled_review

    completed, completed_parsed, completed_review = parse_timestamp_to_iso(row.get("completed_at"))
    cleaned["completed_at"] = completed
    cleaned["_completed_parsed"] = completed_parsed
    needs_review = needs_review or completed_review

    status, standardized, review = normalize_vocabulary(row.get("interview_status"), INTERVIEW_STATUS_MAP)
    cleaned["interview_status"] = status
    cleaned["_status_standardized"] = standardized
    needs_review = needs_review or review

    recommendation, standardized, review = normalize_vocabulary(row.get("recommendation"), INTERVIEW_RECOMMENDATION_MAP)
    cleaned["recommendation"] = recommendation
    cleaned["_recommendation_standardized"] = standardized
    needs_review = needs_review or review

    for field in ("technical_score", "communication_score", "overall_score"):
        value = row.get(field)
        if value in (None, ""):
            cleaned[field] = None
            continue
        normalized, standardized, review = normalize_decimal_text(value)
        cleaned[field] = normalized
        cleaned[f"_{field}_standardized"] = standardized
        needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_offer_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["offer_id"] = clean_string(row.get("offer_id"))
    cleaned["application_id"] = clean_string(row.get("application_id"))
    cleaned["candidate_id"] = clean_string(row.get("candidate_id"))
    cleaned["offered_role"] = clean_string(row.get("offered_role"))
    cleaned["currency"] = clean_string(row.get("currency"))
    cleaned["offer_rejection_reason"] = clean_string(row.get("offer_rejection_reason"))

    offer_date, parsed, review = parse_date_to_iso(row.get("offer_date"))
    cleaned["offer_date"] = offer_date
    cleaned["_offer_date_parsed"] = parsed
    needs_review = needs_review or review

    joining_date, parsed, review = parse_date_to_iso(row.get("joining_date"))
    cleaned["joining_date"] = joining_date
    cleaned["_joining_date_parsed"] = parsed
    needs_review = needs_review or review

    response_date, parsed, review = parse_date_to_iso(row.get("response_date"))
    cleaned["response_date"] = response_date
    cleaned["_response_date_parsed"] = parsed
    needs_review = needs_review or review

    status, standardized, review = normalize_vocabulary(row.get("offer_status"), OFFER_STATUS_MAP)
    cleaned["offer_status"] = status
    cleaned["_status_standardized"] = standardized
    needs_review = needs_review or review

    salary, standardized, review = normalize_decimal_text(row.get("offered_salary"))
    cleaned["offered_salary"] = salary
    cleaned["_salary_standardized"] = standardized
    needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_onboarding_record(row: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    cleaned = row.copy()
    needs_review = False

    cleaned["onboarding_id"] = clean_string(row.get("onboarding_id"))
    cleaned["offer_id"] = clean_string(row.get("offer_id"))
    cleaned["application_id"] = clean_string(row.get("application_id"))
    cleaned["candidate_id"] = clean_string(row.get("candidate_id"))
    cleaned["no_join_reason"] = clean_string(row.get("no_join_reason"))

    planned, parsed, review = parse_date_to_iso(row.get("planned_joining_date"))
    cleaned["planned_joining_date"] = planned
    cleaned["_planned_joining_date_parsed"] = parsed
    needs_review = needs_review or review

    actual, parsed, review = parse_date_to_iso(row.get("actual_joining_date"))
    cleaned["actual_joining_date"] = actual
    cleaned["_actual_joining_date_parsed"] = parsed
    needs_review = needs_review or review

    status, standardized, review = normalize_vocabulary(row.get("joining_status"), JOINING_STATUS_MAP)
    cleaned["joining_status"] = status
    cleaned["_status_standardized"] = standardized
    needs_review = needs_review or review

    onboarding_completed, standardized, review = normalize_boolean_text(row.get("onboarding_completed"))
    cleaned["onboarding_completed"] = onboarding_completed
    cleaned["_onboarding_completed_standardized"] = standardized
    needs_review = needs_review or review

    return cleaned, "review" if needs_review else "cleaned"


def clean_batch(batch_id: str) -> Dict[str, int]:
    """
    Reads validated staging records for a batch, applies deterministic cleaning,
    and marks each staging row as cleaned or review.
    """
    clean_counts = {}

    cleaners = {
        "candidates": (clean_candidate_record, "staging.candidates"),
        "jobs": (clean_job_record, "staging.jobs"),
        "applications": (clean_application_record, "staging.applications"),
        "stage_events": (clean_stage_event_record, "staging.stage_events"),
        "interviews": (clean_interview_record, "staging.interviews"),
        "offers": (clean_offer_record, "staging.offers"),
        "onboarding": (clean_onboarding_record, "staging.onboarding"),
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            for entity_type, (cleaner_func, table_name) in cleaners.items():
                cur.execute(
                    f"""
                    SELECT *
                    FROM {table_name}
                    WHERE ingestion_batch_id = %s
                      AND validation_status IN ('valid', 'warning')
                      AND COALESCE(cleaned_status, 'pending') <> 'cleaned'
                    ORDER BY source_row_number, staging_record_id
                    """,
                    (batch_id,),
                )
                records = cur.fetchall()

                if not records:
                    clean_counts[entity_type] = 0
                    continue

                columns = [desc[0] for desc in cur.description]
                columns_set = set(columns)
                cleaned_count = 0

                mutable_columns = {
                    "candidate_id",
                    "email",
                    "original_email",
                    "first_name",
                    "last_name",
                    "phone",
                    "job_id",
                    "job_title",
                    "department",
                    "location",
                    "employment_type",
                    "application_id",
                    "candidate_id",
                    "job_id",
                    "application_date",
                    "source",
                    "stage_event_id",
                    "application_id",
                    "stage_name",
                    "entered_at",
                    "exited_at",
                    "stage_outcome",
                    "dropoff_flag",
                    "dropoff_reason",
                    "interview_id",
                    "application_id",
                    "candidate_id",
                    "interview_type",
                    "scheduled_at",
                    "completed_at",
                    "interview_status",
                    "technical_score",
                    "communication_score",
                    "overall_score",
                    "recommendation",
                    "feedback",
                    "offer_id",
                    "application_id",
                    "candidate_id",
                    "offer_date",
                    "offered_role",
                    "offered_salary",
                    "currency",
                    "joining_date",
                    "offer_status",
                    "response_date",
                    "offer_rejection_reason",
                    "onboarding_id",
                    "offer_id",
                    "application_id",
                    "candidate_id",
                    "planned_joining_date",
                    "actual_joining_date",
                    "joining_status",
                    "no_join_reason",
                    "onboarding_completed",
                }

                for record in records:
                    row = dict(zip(columns, record))
                    staging_id = row["staging_record_id"]

                    cleaned_row, cleaned_status = cleaner_func(row)

                    update_fields = []
                    update_values = []

                    for key, value in cleaned_row.items():
                        if key.startswith("_"):
                            if key in columns_set:
                                update_fields.append(f"{key} = %s")
                                update_values.append(value)
                            continue

                        if key in mutable_columns and key in columns_set:
                            update_fields.append(f"{key} = %s")
                            update_values.append(value)

                    if "cleaned_status" in columns_set:
                        update_fields.append("cleaned_status = %s")
                        update_values.append(cleaned_status)

                    if "cleaned_at" in columns_set:
                        update_fields.append("cleaned_at = NOW()")

                    if update_fields:
                        query = f"""
                            UPDATE {table_name}
                            SET {", ".join(update_fields)}
                            WHERE staging_record_id = %s
                        """
                        update_values.append(staging_id)
                        cur.execute(query, update_values)
                        cleaned_count += 1

                clean_counts[entity_type] = cleaned_count
                print(f"Cleaned {cleaned_count} {entity_type} records")

            cur.execute(
                """
                UPDATE core.ingestion_batches
                SET status = 'cleaned'
                WHERE id = %s
                """,
                (batch_id,),
            )
            conn.commit()

    return clean_counts
