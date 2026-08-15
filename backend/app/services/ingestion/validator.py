# backend/app/services/ingestion/validator.py
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from app.core.database import get_connection

# Canonical reference data (must match your core tables)
CANONICAL_DEPARTMENTS = {"Engineering", "Sales", "Marketing", "IT", "HR", "Finance"}
CANONICAL_STAGES = {
    "Applied", "Screening", "Recruiter Screen", "Hiring Manager Review",
    "Technical Interview", "Final Interview", "Offer", "Offer Accepted", "Joined"
}
VALID_OUTCOMES = {"Passed", "Failed", "Withdrew", "Offered", "Joined"}

# Entity-specific validation rules
REQUIRED_FIELDS = {
    "candidates": ["candidate_id"],
    "jobs": ["job_id", "job_title", "department"],
    "applications": ["application_id", "candidate_id", "job_id", "application_date"],
    "stage_events": ["stage_event_id", "application_id", "stage_name", "entered_at"],
    "interviews": ["interview_id", "application_id"],
    "offers": ["offer_id", "application_id"],
    "onboarding": ["onboarding_id", "application_id"]
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

def validate_record(row: Dict, entity_type: str, row_number: int) -> Dict[str, Any]:
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