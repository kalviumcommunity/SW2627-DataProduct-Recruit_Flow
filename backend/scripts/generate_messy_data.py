# backend/scripts/generate_messy_data.py
import os
import csv
import random
import json
from copy import deepcopy
from datetime import datetime

# Import the clean generators so we don't rewrite logic
from generate_clean_data import (
    generate_candidates, generate_jobs, generate_applications, 
    generate_stage_events, generate_interviews, generate_offers, generate_onboarding
)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def introduce_chaos(rows, chaos_config):
    """
    Applies mutations to a list of dicts based on the chaos_config.
    chaos_config is a dict: {field_name: [list_of_possible_mutations]}
    """
    for row in rows:
        for field, mutations in chaos_config.items():
            if field in row and random.random() < 0.3:  # 30% chance of mutation
                mutation = random.choice(mutations)
                if callable(mutation):
                    row[field] = mutation(row[field])
                else:
                    row[field] = mutation
    return rows

# --- Define the Chaos Mutations ---
def add_spaces(val):
    return f" {val} " if isinstance(val, str) else val

def lower_case(val):
    return val.lower() if isinstance(val, str) else val

def upper_case(val):
    return val.upper() if isinstance(val, str) else val

def swap_date_format(val):
    """Turns YYYY-MM-DD into MM/DD/YYYY"""
    if isinstance(val, str) and "-" in val:
        parts = val.split("-")
        if len(parts) == 3:
            return f"{parts[1]}/{parts[2]}/{parts[0]}"
    return val

def make_ambiguous_date(val):
    """Turns 2024-01-15 into 01/15/2024 (US) or 15/01/2024 (EU)"""
    if isinstance(val, str) and "-" in val:
        parts = val.split("-")
        if len(parts) == 3:
            return random.choice([f"{parts[1]}/{parts[2]}/{parts[0]}", f"{parts[2]}/{parts[1]}/{parts[0]}"])
    return val

def nullify(val):
    return None

def duplicate_identity(val):
    """Adds a prefix to candidate_id to simulate a different source system"""
    return f"SRC2-{val}" if val else val

def weird_status(val):
    choices = [val, lower_case(val), upper_case(val), "Done", "Rejected", "Offer accepted", "No hire", "Joined"]
    return random.choice(choices)

def messy_score(val):
    choices = [val, "N/A", "foo", "NaN", "  ", None, f" {val} " if val is not None else None]
    return random.choice(choices)

def currency_noise(val):
    choices = [val, val.lower() if isinstance(val, str) else val, f" ${val} " if val is not None else None, "usd", "US Dollars"]
    return random.choice(choices)

# --- Chaos Configurations per Entity ---
CANDIDATE_CHAOS = {
    "email": [nullify, lambda x: x.upper() if x else None, add_spaces],
    "first_name": [add_spaces, lower_case],
    "last_name": [add_spaces, lower_case],
}

JOB_CHAOS = {
    "department": [add_spaces, lower_case, upper_case, 
                   lambda x: "IT" if x == "Engineering" else x,  # Wrong mapping
                   lambda x: "Information Technology" if x == "IT" else x]
}

APPLICATION_CHAOS = {
    "application_date": [swap_date_format, make_ambiguous_date],
    "candidate_id": [lambda x: None if random.random() > 0.8 else x]  # 20% missing
}

STAGE_EVENT_CHAOS = {
    "stage_name": [add_spaces, lower_case,
                   lambda x: "Tech Interview" if x == "Technical Interview" else x,
                   lambda x: "HR Round" if x == "Final Interview" else x],
    "entered_at": [swap_date_format],
    "exited_at": [swap_date_format, nullify]
}

INTERVIEW_CHAOS = {
    "interview_type": [add_spaces, lower_case, lambda x: "HR Round", lambda x: "Final Panel"],
    "scheduled_at": [swap_date_format],
    "completed_at": [swap_date_format, nullify],
    "interview_status": [weird_status],
    "technical_score": [messy_score],
    "communication_score": [messy_score],
    "overall_score": [messy_score],
    "recommendation": [lambda x: random.choice(["Strong Hire", "Hire", "Leaning No", "No Hire", "Maybe", ""]), lower_case],
    "feedback": [add_spaces, nullify]
}

OFFER_CHAOS = {
    "offer_date": [swap_date_format],
    "joining_date": [swap_date_format, nullify],
    "offer_status": [weird_status],
    "offered_role": [add_spaces, lower_case],
    "offered_salary": [lambda x: f"${x}" if random.random() > 0.5 else x, lambda x: f"{x:,}" if isinstance(x, int) else x],
    "currency": [currency_noise],
    "response_date": [swap_date_format, nullify],
    "offer_rejection_reason": [add_spaces, nullify, lambda x: "Competing Offer"]
}

ONBOARDING_CHAOS = {
    "planned_joining_date": [swap_date_format],
    "actual_joining_date": [swap_date_format, nullify],
    "joining_status": [weird_status],
    "no_join_reason": [add_spaces, nullify, lambda x: "Found other offer"],
    "onboarding_completed": [lambda x: "YES" if random.random() > 0.5 else "No", lambda x: "true" if random.random() > 0.5 else "false"]
}

def write_csv(filename, headers, rows):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Generated (Messy): {filename}")

if __name__ == "__main__":
    print("🌀 Generating MESSY Dataset (With deliberate errors)...")
    
    # Step 1: Generate clean base data
    candidates = generate_candidates(50)
    jobs = generate_jobs(5)
    applications = generate_applications(candidates, jobs, 80)
    stage_events, final_stage_per_app = generate_stage_events(applications)
    interviews = generate_interviews(applications, final_stage_per_app)
    offers = generate_offers(applications, final_stage_per_app)
    onboarding = generate_onboarding(offers)
    
    # Step 2: Introduce chaos
    candidates = introduce_chaos(candidates, CANDIDATE_CHAOS)
    jobs = introduce_chaos(jobs, JOB_CHAOS)
    applications = introduce_chaos(applications, APPLICATION_CHAOS)
    stage_events = introduce_chaos(stage_events, STAGE_EVENT_CHAOS)
    interviews = introduce_chaos(interviews, INTERVIEW_CHAOS)
    offers = introduce_chaos(offers, OFFER_CHAOS)
    onboarding = introduce_chaos(onboarding, ONBOARDING_CHAOS)
    
    # Step 3: Intentionally duplicate some candidates (for deduplication testing)
    # Take the first candidate and duplicate them with a different ID
    if len(candidates) > 5:
        dup = deepcopy(candidates[0])
        dup["candidate_id"] = "CAND-DUP-0001"
        dup["email"] = candidates[1]["email"]  # Same email as another candidate
        candidates.append(dup)
    
    # Step 4: Write the messy CSVs
    write_csv("messy_candidates.csv", ["candidate_id", "email", "first_name", "last_name", "phone"], candidates)
    write_csv("messy_jobs.csv", ["job_id", "job_title", "department", "location", "employment_type"], jobs)
    write_csv("messy_applications.csv", ["application_id", "candidate_id", "job_id", "application_date", "source"], applications)
    write_csv("messy_stage_events.csv", ["stage_event_id", "application_id", "stage_name", "entered_at", "exited_at", "stage_outcome", "dropoff_flag", "dropoff_reason"], stage_events)
    write_csv("messy_interviews.csv", ["interview_id", "application_id", "candidate_id", "interview_type", "scheduled_at", "completed_at", "interview_status", "technical_score", "communication_score", "overall_score", "recommendation", "feedback"], interviews)
    write_csv("messy_offers.csv", ["offer_id", "application_id", "candidate_id", "offer_date", "offered_role", "offered_salary", "currency", "joining_date", "offer_status", "response_date", "offer_rejection_reason"], offers)
    write_csv("messy_onboarding.csv", ["onboarding_id", "offer_id", "application_id", "candidate_id", "planned_joining_date", "actual_joining_date", "joining_status", "no_join_reason", "onboarding_completed"], onboarding)
    
    # Step 5: Generate the "Expected Results" JSON (The Truth Serum)
    stage_counts = {}
    for row in stage_events:
        stage_counts[row["stage_name"]] = stage_counts.get(row["stage_name"], 0) + 1

    expected = {
        "total_applications": len(applications),
        "total_candidates": len(set([c["candidate_id"] for c in candidates])),
        "total_interviews": len(interviews),
        "total_offers": len(offers),
        "total_onboarding": len(onboarding),
        "expected_dropoff_stage": max(stage_counts, key=stage_counts.get),  # The densest stage acts as our likely bottleneck
        "top_department": "Engineering",
        "duplicate_candidates": 1,  # We injected one duplicate
        "stage_counts": stage_counts,
        "supported_entities": {
            "interviews": len(interviews),
            "offers": len(offers),
            "onboarding": len(onboarding),
        }
    }
    
    with open(os.path.join(os.path.dirname(__file__), "expected_results.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=2)
    
    print("🎉 Messy dataset and expected_results.json generated!")
