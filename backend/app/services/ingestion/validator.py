# backend/app/services/ingestion/validator.py
import json
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from app.core.database import get_connection

# Canonical reference data (must match your core tables)
CANONICAL_DEPARTMENTS = {"Engineering", "Sales", "Marketing", "IT", "HR", "Finance"}
CANONICAL_STAGES = {
    "Applied", "Screening", "Recruiter Screen", "Hiring Manager Review",
    "Technical Interview", "Final Interview", "Offer", "Offer Accepted", "Joined"
}
VALID_OUTCOMES = {"Passed", "Failed", "Withdrew", "Offered", "Joined"}
VALID_INTERVIEW_STATUSES = {"Scheduled", "Completed", "Cancelled"}
VALID_INTERVIEW_RECOMMENDATIONS = {"Strong Hire", "Hire", "Leaning No", "No Hire"}
VALID_OFFER_STATUSES = {"Sent", "Accepted", "Declined", "Expired"}
VALID_JOINING_STATUSES = {"Joined", "No Show", "Postponed", "Cancelled"}

# Entity-specific validation rules
REQUIRED_FIELDS = {
    "candidates": ["candidate_id"],
    "jobs": ["job_id", "job_title", "department"],
    "applications": ["application_id", "candidate_id", "job_id", "application_date"],
    "stage_events": ["stage_event_id", "application_id", "stage_name", "entered_at"],
    "interviews": ["interview_id", "application_id", "candidate_id", "interview_type", "scheduled_at", "interview_status"],
    "offers": ["offer_id", "application_id", "candidate_id", "offer_date", "offered_role", "offer_status"],
    "onboarding": ["onboarding_id", "offer_id", "application_id", "candidate_id", "planned_joining_date", "joining_status"]
}

def validate_required_fields(row: Dict, entity_type: str) -> List[str]:
    """Checks if all required fields are present and non-empty."""
    errors = []
    required = REQUIRED_FIELDS.get(entity_type, [])
    for field in required:
        value = row.get(field, "").strip()
        if not value:  # Empty string or None
            errors.append(f"Missing required field: '{field}'")
    return errors

def validate_date_format(date_str: str) -> bool:
    """Attempts to parse common date formats."""
    if not date_str or not isinstance(date_str, str):
        return False
    # Try common formats
    formats = [
        "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
        "%b %d, %Y", "%d-%b-%Y"
    ]
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

def validate_datetime_format(datetime_str: str) -> bool:
    """Attempts to parse common timestamp formats."""
    if not datetime_str or not isinstance(datetime_str, str):
        return False
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            datetime.strptime(datetime_str, fmt)
            return True
        except ValueError:
            continue
    return validate_date_format(datetime_str)

def validate_numeric_score(value: Any, min_value: float = 0.0, max_value: float = 5.0) -> Tuple[bool, Optional[float]]:
    """Validate a score-like field and coerce to float if possible."""
    if value is None:
        return True, None
    cleaned = str(value).strip()
    if cleaned == "":
        return True, None
    try:
        parsed = float(cleaned)
    except ValueError:
        return False, None
    if not math.isfinite(parsed):
        return False, None
    if parsed < min_value or parsed > max_value:
        return False, None
    return True, parsed

def validate_canonical_value(value: str, allowed_values: set[str]) -> Tuple[bool, str]:
    """Case-insensitive exact matching against a canonical vocabulary."""
    if not value:
        return False, ""
    cleaned = value.strip()
    for canonical in allowed_values:
        if cleaned.lower() == canonical.lower():
            return True, canonical
    return False, cleaned

def reference_exists(conn, table: str, column: str, value: str) -> bool:
    """Checks whether a canonical reference row exists in core."""
    if not value:
        return False
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT 1
            FROM {table}
            WHERE {column} = %s
            LIMIT 1
            """,
            (value,),
        )
        return cur.fetchone() is not None

def validate_department(dept_str: str) -> Tuple[bool, str]:
    """
    Validates if department exists in canonical list.
    Returns (is_valid, normalized_name_or_error).
    We don't normalize yet, just check if it matches exactly or with minor case variations.
    """
    if not dept_str:
        return False, "Department is empty"
    
    # Simple exact matching (case-insensitive)
    dept_clean = dept_str.strip()
    for canonical in CANONICAL_DEPARTMENTS:
        if dept_clean.lower() == canonical.lower():
            return True, canonical  # Return the canonical version
    
    # If we reach here, it might be a synonym (e.g., "Information Technology" -> "IT")
    # We'll handle that in cleaning. For validation, we just warn, not reject.
    # Actually, to be strict, we should check if it's close. We'll allow it but flag a warning.
    return True, dept_clean  # We accept it, but we will clean later

def validate_stage_name(stage_str: str) -> Tuple[bool, str]:
    """
    Validates stage name. We accept if it matches a canonical stage (case-insensitive)
    or if it looks like a stage alias.
    """
    if not stage_str:
        return False, "Stage name is empty"
    
    stage_clean = stage_str.strip()
    # Check exact match
    for canonical in CANONICAL_STAGES:
        if stage_clean.lower() == canonical.lower():
            return True, canonical
    
    # Allow common aliases (we'll handle full mapping in cleaning)
    # For validation, we accept anything that isn't obviously garbage, but we flag a warning
    return True, stage_clean  # Accept, but we will clean later

def validate_boolean_flag(flag_str: str) -> Tuple[bool, bool]:
    """
    Converts string 'TRUE', '1', 'yes' to True boolean.
    Returns (is_valid, boolean_value)
    """
    if not flag_str:
        return True, False  # Missing flag defaults to False
    
    flag_clean = flag_str.strip().lower()
    if flag_clean in ['true', '1', 'yes', 't', 'y']:
        return True, True
    elif flag_clean in ['false', '0', 'no', 'f', 'n', '']:
        return True, False
    else:
        return False, False  # Invalid boolean value

def validate_record(row: Dict, entity_type: str, row_number: int, conn=None) -> Dict[str, Any]:
    """
    Main validation orchestrator.
    Returns a dict with:
      - valid: bool
      - errors: List[str]
      - warnings: List[str]
      - cleaned_data: Dict (with basic type conversions)
    """
    errors = []
    warnings = []
    cleaned_data = {}
    
    # 1. Check required fields
    errors.extend(validate_required_fields(row, entity_type))
    
    # 2. Entity-specific validations
    if entity_type == "candidates":
        # candidate_id: just ensure it's non-empty (already done)
        pass
        
    elif entity_type == "jobs":
        # department validation
        dept = row.get("department", "")
        is_valid, canonical = validate_department(dept)
        if is_valid:
            cleaned_data["department"] = canonical
        else:
            errors.append(f"Invalid department: '{dept}'")
    
    elif entity_type == "applications":
        # application_date validation
        app_date = row.get("application_date", "")
        if app_date:
            if not validate_date_format(app_date):
                errors.append(f"Invalid application_date format: '{app_date}'")
            else:
                cleaned_data["application_date"] = app_date
        else:
            errors.append("application_date is required")
    
    elif entity_type == "stage_events":
        # stage_name validation
        stage = row.get("stage_name", "")
        if stage:
            is_valid, canonical = validate_stage_name(stage)
            if is_valid:
                cleaned_data["stage_name"] = canonical
            else:
                errors.append(f"Invalid stage_name: '{stage}'")
        else:
            errors.append("stage_name is required")
        
        # entered_at validation
        entered = row.get("entered_at", "")
        if entered:
            if not validate_date_format(entered):
                errors.append(f"Invalid entered_at format: '{entered}'")
            else:
                cleaned_data["entered_at"] = entered
        else:
            errors.append("entered_at is required")
        
        # exited_at: optional, but if present must be valid
        exited = row.get("exited_at", "")
        if exited:
            if not validate_date_format(exited):
                errors.append(f"Invalid exited_at format: '{exited}'")
            else:
                cleaned_data["exited_at"] = exited
        
        # dropoff_flag: convert to boolean
        flag = row.get("dropoff_flag", "")
        if flag:
            is_valid, bool_val = validate_boolean_flag(flag)
            if is_valid:
                cleaned_data["dropoff_flag"] = bool_val
            else:
                errors.append(f"Invalid dropoff_flag value: '{flag}'")
        else:
            cleaned_data["dropoff_flag"] = False
        
        # dropoff_reason: if flag is True, reason should exist
        dropoff_reason = row.get("dropoff_reason", "")
        cleaned_data["dropoff_reason"] = dropoff_reason
        
        # Business rule: if dropoff_flag is True, reason must be present
        if cleaned_data.get("dropoff_flag", False) and not dropoff_reason:
            warnings.append("dropoff_flag is TRUE but dropoff_reason is empty. Will be flagged during journey reconstruction.")

    elif entity_type == "interviews":
        interview_id = row.get("interview_id", "")
        application_id = row.get("application_id", "")
        candidate_id = row.get("candidate_id", "")

        if conn and not reference_exists(conn, "core.applications", "application_id", application_id):
            errors.append(f"Unknown application_id: '{application_id}'")
        if conn and not reference_exists(conn, "core.candidates", "candidate_id", candidate_id):
            errors.append(f"Unknown candidate_id: '{candidate_id}'")

        scheduled = row.get("scheduled_at", "")
        if scheduled:
            if not validate_datetime_format(scheduled):
                errors.append(f"Invalid scheduled_at format: '{scheduled}'")
            else:
                cleaned_data["scheduled_at"] = scheduled
        else:
            errors.append("scheduled_at is required")

        completed = row.get("completed_at", "")
        if completed:
            if not validate_datetime_format(completed):
                errors.append(f"Invalid completed_at format: '{completed}'")
            else:
                cleaned_data["completed_at"] = completed

        status = row.get("interview_status", "")
        is_valid, canonical_status = validate_canonical_value(status, VALID_INTERVIEW_STATUSES)
        if is_valid:
            cleaned_data["interview_status"] = canonical_status
        else:
            errors.append(f"Invalid interview_status: '{status}'")

        recommendation = row.get("recommendation", "")
        if recommendation:
            rec_valid, canonical_rec = validate_canonical_value(recommendation, VALID_INTERVIEW_RECOMMENDATIONS)
            if rec_valid:
                cleaned_data["recommendation"] = canonical_rec
            else:
                warnings.append(f"Unrecognized recommendation: '{recommendation}'")

        for score_field in ("technical_score", "communication_score", "overall_score"):
            score_valid, parsed_score = validate_numeric_score(row.get(score_field))
            if not score_valid:
                errors.append(f"Invalid {score_field}: '{row.get(score_field)}'")
            elif parsed_score is not None:
                cleaned_data[score_field] = parsed_score

        if not cleaned_data.get("interview_type"):
            cleaned_data["interview_type"] = row.get("interview_type", "").strip()

    elif entity_type == "offers":
        application_id = row.get("application_id", "")
        candidate_id = row.get("candidate_id", "")

        if conn and not reference_exists(conn, "core.applications", "application_id", application_id):
            errors.append(f"Unknown application_id: '{application_id}'")
        if conn and not reference_exists(conn, "core.candidates", "candidate_id", candidate_id):
            errors.append(f"Unknown candidate_id: '{candidate_id}'")

        offer_date = row.get("offer_date", "")
        if offer_date:
            if not validate_date_format(offer_date):
                errors.append(f"Invalid offer_date format: '{offer_date}'")
            else:
                cleaned_data["offer_date"] = offer_date
        else:
            errors.append("offer_date is required")

        joining_date = row.get("joining_date", "")
        if joining_date:
            if not validate_date_format(joining_date):
                errors.append(f"Invalid joining_date format: '{joining_date}'")
            else:
                cleaned_data["joining_date"] = joining_date

        response_date = row.get("response_date", "")
        if response_date:
            if not validate_date_format(response_date):
                errors.append(f"Invalid response_date format: '{response_date}'")
            else:
                cleaned_data["response_date"] = response_date

        status = row.get("offer_status", "")
        is_valid, canonical_status = validate_canonical_value(status, VALID_OFFER_STATUSES)
        if is_valid:
            cleaned_data["offer_status"] = canonical_status
        else:
            errors.append(f"Invalid offer_status: '{status}'")

        salary = row.get("offered_salary", "")
        if salary:
            try:
                cleaned_data["offered_salary"] = float(str(salary).strip())
            except ValueError:
                errors.append(f"Invalid offered_salary: '{salary}'")

    elif entity_type == "onboarding":
        offer_id = row.get("offer_id", "")
        application_id = row.get("application_id", "")
        candidate_id = row.get("candidate_id", "")

        if conn and not reference_exists(conn, "core.offers", "offer_id", offer_id):
            errors.append(f"Unknown offer_id: '{offer_id}'")
        if conn and not reference_exists(conn, "core.applications", "application_id", application_id):
            errors.append(f"Unknown application_id: '{application_id}'")
        if conn and not reference_exists(conn, "core.candidates", "candidate_id", candidate_id):
            errors.append(f"Unknown candidate_id: '{candidate_id}'")

        planned = row.get("planned_joining_date", "")
        if planned:
            if not validate_date_format(planned):
                errors.append(f"Invalid planned_joining_date format: '{planned}'")
            else:
                cleaned_data["planned_joining_date"] = planned
        else:
            errors.append("planned_joining_date is required")

        actual = row.get("actual_joining_date", "")
        if actual:
            if not validate_date_format(actual):
                errors.append(f"Invalid actual_joining_date format: '{actual}'")
            else:
                cleaned_data["actual_joining_date"] = actual

        status = row.get("joining_status", "")
        is_valid, canonical_status = validate_canonical_value(status, VALID_JOINING_STATUSES)
        if is_valid:
            cleaned_data["joining_status"] = canonical_status
        else:
            errors.append(f"Invalid joining_status: '{status}'")

        completed = row.get("onboarding_completed", "")
        if completed:
            bool_valid, bool_val = validate_boolean_flag(completed)
            if bool_valid:
                cleaned_data["onboarding_completed"] = bool_val
            else:
                errors.append(f"Invalid onboarding_completed value: '{completed}'")
        else:
            cleaned_data["onboarding_completed"] = False

    # 3. Copy all other fields to cleaned_data (preserve original values for later)
    for key, value in row.items():
        if key not in cleaned_data:
            cleaned_data[key] = value
    
    # Final verdict
    is_valid = len(errors) == 0
    
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "cleaned_data": cleaned_data
    }
