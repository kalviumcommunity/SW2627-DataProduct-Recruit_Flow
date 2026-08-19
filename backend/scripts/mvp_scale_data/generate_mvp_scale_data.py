import csv
import argparse
import json
import os
import random
import sys
from datetime import datetime
from copy import deepcopy
from secrets import token_hex

CURRENT_DIR = os.path.dirname(__file__)
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import generate_clean_data as clean_gen
import generate_messy_data as messy_gen

SEED = 42

OUTPUT_ROOT = os.path.join(CURRENT_DIR, "outputs")
CLEAN_DIR = os.path.join(OUTPUT_ROOT, "clean")
MESSY_DIR = os.path.join(OUTPUT_ROOT, "messy")

CLEAN_COUNTS = {
    "candidates": 5000,
    "jobs": 250,
    "applications": 25000,
}

BOTTLE_NECK_PROFILE = {
    "stage_weights": [9, 13, 16, 18, 14, 10, 6, 3, 1],
    "pre_offer_outcome_weights": [45, 35, 20],
    "offer_plus_outcome_weights": [50, 30, 20],
    "interview_status_weights": [28, 52, 20],
    "partial_interview_boost": 0.45,
    "offer_status_weights": [25, 35, 30, 10],
    "joining_status_weights": [35, 25, 20, 20],
    "onboarding_completed_weights": [50, 50],
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv(output_dir: str, filename: str, headers, rows) -> None:
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def seed_all() -> None:
    random.seed(SEED)
    clean_gen.random.seed(SEED)
    messy_gen.random.seed(SEED)
    clean_gen.Faker.seed(SEED)
    clean_gen.fake.seed_instance(SEED)


def make_run_namespace(label: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{label}-{timestamp}-{token_hex(3)}"


def namespace_entities(candidates, jobs, applications, stage_events, interviews, offers, onboarding, namespace):
    candidate_map = {}
    for idx, row in enumerate(candidates, start=1):
        old_id = row["candidate_id"]
        new_id = f"{namespace}-CAND-{idx:05d}"
        candidate_map[old_id] = new_id
        if row.get("email") and "@" in row["email"]:
            local_part, domain = row["email"].split("@", 1)
        else:
            local_part, domain = f"candidate-{idx:05d}", "example.com"
        row["candidate_id"] = new_id
        row["email"] = f"{namespace.lower()}.{local_part}@{domain}"
        row["phone"] = f"+1-{namespace[-6:].replace('-', '')}-{idx:07d}"

    job_map = {}
    for idx, row in enumerate(jobs, start=1):
        old_id = row["job_id"]
        new_id = f"{namespace}-JOB-{idx:05d}"
        job_map[old_id] = new_id
        row["job_id"] = new_id

    application_map = {}
    for idx, row in enumerate(applications, start=1):
        old_id = row["application_id"]
        new_id = f"{namespace}-APP-{idx:06d}"
        application_map[old_id] = new_id
        row["application_id"] = new_id
        row["candidate_id"] = candidate_map.get(row.get("candidate_id"), row.get("candidate_id"))
        row["job_id"] = job_map.get(row.get("job_id"), row.get("job_id"))

    for idx, row in enumerate(stage_events, start=1):
        row["stage_event_id"] = f"{namespace}-EVT-{idx:07d}"
        row["application_id"] = application_map.get(row.get("application_id"), row.get("application_id"))

    for idx, row in enumerate(interviews, start=1):
        row["interview_id"] = f"{namespace}-INT-{idx:07d}"
        row["application_id"] = application_map.get(row.get("application_id"), row.get("application_id"))
        row["candidate_id"] = candidate_map.get(row.get("candidate_id"), row.get("candidate_id"))

    offer_map = {}
    for idx, row in enumerate(offers, start=1):
        old_id = row["offer_id"]
        new_id = f"{namespace}-OFF-{idx:06d}"
        offer_map[old_id] = new_id
        row["offer_id"] = new_id
        row["application_id"] = application_map.get(row.get("application_id"), row.get("application_id"))
        row["candidate_id"] = candidate_map.get(row.get("candidate_id"), row.get("candidate_id"))

    for idx, row in enumerate(onboarding, start=1):
        row["onboarding_id"] = f"{namespace}-ONB-{idx:06d}"
        row["offer_id"] = offer_map.get(row.get("offer_id"), row.get("offer_id"))
        row["application_id"] = application_map.get(row.get("application_id"), row.get("application_id"))
        row["candidate_id"] = candidate_map.get(row.get("candidate_id"), row.get("candidate_id"))

    return {
        "candidates": len(candidates),
        "jobs": len(jobs),
        "applications": len(applications),
        "stage_events": len(stage_events),
        "interviews": len(interviews),
        "offers": len(offers),
        "onboarding": len(onboarding),
    }


def build_clean_dataset(namespace: str) -> dict:
    seed_all()
    ensure_dir(CLEAN_DIR)

    candidates = clean_gen.generate_candidates(CLEAN_COUNTS["candidates"])
    jobs = clean_gen.generate_jobs(CLEAN_COUNTS["jobs"])
    applications = clean_gen.generate_applications(
        candidates,
        jobs,
        CLEAN_COUNTS["applications"],
    )
    stage_events, final_stage_per_app = clean_gen.generate_stage_events(
        applications,
        profile=BOTTLE_NECK_PROFILE,
    )
    interviews = clean_gen.generate_interviews(
        applications,
        final_stage_per_app,
        profile=BOTTLE_NECK_PROFILE,
    )
    offers = clean_gen.generate_offers(
        applications,
        final_stage_per_app,
        profile=BOTTLE_NECK_PROFILE,
    )
    onboarding = clean_gen.generate_onboarding(offers, profile=BOTTLE_NECK_PROFILE)

    applications_reaching_offer = sum(
        1
        for app in applications
        if app["application_id"] in final_stage_per_app
        and final_stage_per_app[app["application_id"]]["final_stage"]
        in {"Offer", "Offer Accepted", "Joined"}
    )
    applications_reaching_joined = sum(
        1 for row in onboarding if row["joining_status"] == "Joined"
    )

    raw_summary = namespace_entities(
        candidates, jobs, applications, stage_events, interviews, offers, onboarding, namespace
    )

    summary = {
        **raw_summary,
        "applications_reaching_offer": applications_reaching_offer,
        "applications_reaching_joined": applications_reaching_joined,
    }

    write_csv(
        CLEAN_DIR,
        "candidates.csv",
        ["candidate_id", "email", "first_name", "last_name", "phone"],
        candidates,
    )
    write_csv(
        CLEAN_DIR,
        "jobs.csv",
        ["job_id", "job_title", "department", "location", "employment_type"],
        jobs,
    )
    write_csv(
        CLEAN_DIR,
        "applications.csv",
        ["application_id", "candidate_id", "job_id", "application_date", "source"],
        applications,
    )
    write_csv(
        CLEAN_DIR,
        "stage_events.csv",
        [
            "stage_event_id",
            "application_id",
            "stage_name",
            "entered_at",
            "exited_at",
            "stage_outcome",
            "dropoff_flag",
            "dropoff_reason",
        ],
        stage_events,
    )
    write_csv(
        CLEAN_DIR,
        "interviews.csv",
        [
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
        ],
        interviews,
    )
    write_csv(
        CLEAN_DIR,
        "offers.csv",
        [
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
        ],
        offers,
    )
    write_csv(
        CLEAN_DIR,
        "onboarding.csv",
        [
            "onboarding_id",
            "offer_id",
            "application_id",
            "candidate_id",
            "planned_joining_date",
            "actual_joining_date",
            "joining_status",
            "no_join_reason",
            "onboarding_completed",
        ],
        onboarding,
    )

    with open(os.path.join(CLEAN_DIR, "clean_dataset_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def build_messy_dataset(namespace: str) -> dict:
    seed_all()
    ensure_dir(MESSY_DIR)

    candidates = clean_gen.generate_candidates(CLEAN_COUNTS["candidates"])
    jobs = clean_gen.generate_jobs(CLEAN_COUNTS["jobs"])
    applications = clean_gen.generate_applications(
        candidates,
        jobs,
        CLEAN_COUNTS["applications"],
    )
    stage_events, final_stage_per_app = clean_gen.generate_stage_events(
        applications,
        profile=BOTTLE_NECK_PROFILE,
    )
    interviews = clean_gen.generate_interviews(
        applications,
        final_stage_per_app,
        profile=BOTTLE_NECK_PROFILE,
    )
    offers = clean_gen.generate_offers(
        applications,
        final_stage_per_app,
        profile=BOTTLE_NECK_PROFILE,
    )
    onboarding = clean_gen.generate_onboarding(offers, profile=BOTTLE_NECK_PROFILE)

    applications_reaching_offer = sum(
        1
        for app in applications
        if app["application_id"] in final_stage_per_app
        and final_stage_per_app[app["application_id"]]["final_stage"]
        in {"Offer", "Offer Accepted", "Joined"}
    )
    applications_reaching_joined = sum(
        1 for row in onboarding if row["joining_status"] == "Joined"
    )

    candidates = messy_gen.introduce_chaos(candidates, messy_gen.CANDIDATE_CHAOS)
    jobs = messy_gen.introduce_chaos(jobs, messy_gen.JOB_CHAOS)
    applications = messy_gen.introduce_chaos(applications, messy_gen.APPLICATION_CHAOS)
    stage_events = messy_gen.introduce_chaos(stage_events, messy_gen.STAGE_EVENT_CHAOS)
    interviews = messy_gen.introduce_chaos(interviews, messy_gen.INTERVIEW_CHAOS)
    offers = messy_gen.introduce_chaos(offers, messy_gen.OFFER_CHAOS)
    onboarding = messy_gen.introduce_chaos(onboarding, messy_gen.ONBOARDING_CHAOS)

    if len(candidates) > 5:
        dup = deepcopy(candidates[0])
        dup["candidate_id"] = "CAND-DUP-0001"
        dup["email"] = candidates[1]["email"]
        candidates.append(dup)

    raw_summary = namespace_entities(
        candidates, jobs, applications, stage_events, interviews, offers, onboarding, namespace
    )
    if len(candidates) > 5:
        duplicate_email = next((row["email"] for row in candidates if row.get("email")), candidates[0]["email"])
        candidates[-1]["email"] = duplicate_email

    write_csv(
        MESSY_DIR,
        "candidates.csv",
        ["candidate_id", "email", "first_name", "last_name", "phone"],
        candidates,
    )
    write_csv(
        MESSY_DIR,
        "jobs.csv",
        ["job_id", "job_title", "department", "location", "employment_type"],
        jobs,
    )
    write_csv(
        MESSY_DIR,
        "applications.csv",
        ["application_id", "candidate_id", "job_id", "application_date", "source"],
        applications,
    )
    write_csv(
        MESSY_DIR,
        "stage_events.csv",
        [
            "stage_event_id",
            "application_id",
            "stage_name",
            "entered_at",
            "exited_at",
            "stage_outcome",
            "dropoff_flag",
            "dropoff_reason",
        ],
        stage_events,
    )
    write_csv(
        MESSY_DIR,
        "interviews.csv",
        [
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
        ],
        interviews,
    )
    write_csv(
        MESSY_DIR,
        "offers.csv",
        [
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
        ],
        offers,
    )
    write_csv(
        MESSY_DIR,
        "onboarding.csv",
        [
            "onboarding_id",
            "offer_id",
            "application_id",
            "candidate_id",
            "planned_joining_date",
            "actual_joining_date",
            "joining_status",
            "no_join_reason",
            "onboarding_completed",
        ],
        onboarding,
    )

    stage_counts = {}
    for row in stage_events:
        stage_counts[row["stage_name"]] = stage_counts.get(row["stage_name"], 0) + 1

    expected = {
        "total_applications": raw_summary["applications"],
        "total_candidates": len({c["candidate_id"] for c in candidates}),
        "total_interviews": raw_summary["interviews"],
        "total_offers": raw_summary["offers"],
        "total_onboarding": raw_summary["onboarding"],
        "expected_dropoff_stage": max(stage_counts, key=stage_counts.get),
        "top_department": "Engineering",
        "duplicate_candidates": 1,
        "stage_counts": stage_counts,
        "supported_entities": {
            "interviews": len(interviews),
            "offers": len(offers),
            "onboarding": len(onboarding),
        },
        "applications_reaching_offer": applications_reaching_offer,
        "applications_reaching_joined": applications_reaching_joined,
    }

    with open(os.path.join(MESSY_DIR, "expected_results.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=2)

    return expected


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate large MVP datasets with run-specific IDs.")
    parser.add_argument("--run-id", default=None, help="Optional namespace for the generated IDs.")
    args = parser.parse_args()

    run_id = args.run_id or make_run_namespace("mvp")
    ensure_dir(OUTPUT_ROOT)
    clean_summary = build_clean_dataset(f"{run_id}-clean")
    messy_expected = build_messy_dataset(f"{run_id}-messy")

    manifest = {
        "run_id": run_id,
        "clean": {
            "directory": os.path.relpath(CLEAN_DIR, CURRENT_DIR),
            "namespace": f"{run_id}-clean",
            "summary": clean_summary,
        },
        "messy": {
            "directory": os.path.relpath(MESSY_DIR, CURRENT_DIR),
            "namespace": f"{run_id}-messy",
            "expected_results": messy_expected,
        },
    }

    with open(os.path.join(OUTPUT_ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Large-scale MVP dataset generated under:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()
