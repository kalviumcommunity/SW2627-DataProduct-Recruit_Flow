# backend/scripts/generate_clean_data.py
import os
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# --- 1. CONFIGURATION (Adjust these to scale) ---
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

NUM_CANDIDATES = 50
NUM_JOBS = 5
NUM_APPLICATIONS = 80

# Reference Data (MUST match your core tables)
DEPARTMENTS = ["Engineering", "Sales", "Marketing", "IT", "HR", "Finance"]
STAGES = [
    "Applied", "Screening", "Recruiter Screen", "Hiring Manager Review",
    "Technical Interview", "Final Interview", "Offer", "Offer Accepted", "Joined"
]
INTERVIEW_TYPES = ["Phone Screen", "Technical", "Coding Challenge", "Cultural Fit"]
OFFER_STATUSES = ["Sent", "Accepted", "Declined", "Expired"]
JOINING_STATUSES = ["Joined", "No Show", "Postponed", "Cancelled"]

# --- 2. GENERATOR FUNCTIONS ---
def generate_candidates(num):
    candidates = []
    for i in range(1, num + 1):
        first = fake.first_name()
        last = fake.last_name()
        candidates.append({
            "candidate_id": f"CAND-{i:04d}",
            "email": f"{first.lower()}.{last.lower()}@example.com",
            "first_name": first,
            "last_name": last,
            "phone": fake.phone_number()[:15]
        })
    return candidates

def generate_jobs(num):
    jobs = []
    for i in range(1, num + 1):
        dept = random.choice(DEPARTMENTS)
        jobs.append({
            "job_id": f"JOB-{i:04d}",
            "job_title": f"{dept} {fake.job().split()[0]}",
            "department": dept,
            "location": fake.city(),
            "employment_type": random.choice(["Full-time", "Contract"])
        })
    return jobs

def generate_applications(candidates, jobs, num):
    applications = []
    for i in range(1, num + 1):
        app_date = fake.date_between(start_date="-90d", end_date="-1d")
        applications.append({
            "application_id": f"APP-{i:04d}",
            "candidate_id": random.choice(candidates)["candidate_id"],
            "job_id": random.choice(jobs)["job_id"],
            "application_date": app_date.strftime("%Y-%m-%d"),
            "source": random.choice(["LinkedIn", "Referral", "Website"])
        })
    return applications

def generate_stage_events(applications):
    """Generates stage events AND returns the final timeline for each app to be used for interviews/offers."""
    stage_events = []
    final_stage_per_app = {}  # Store the last stage info for each application
    event_id = 1

    for app in applications:
        # Determine max stage index (how far they go in the funnel)
        max_idx = random.choices(
            population=range(1, len(STAGES) + 1),
            weights=[5, 8, 10, 15, 12, 8, 5, 3, 1],
            k=1
        )[0]
        
        current_time = datetime.strptime(app["application_date"], "%Y-%m-%d")
        last_exited_at = None
        last_stage_outcome = None
        
        for stage_idx in range(max_idx):
            stage_name = STAGES[stage_idx]
            is_final = (stage_idx == max_idx - 1)
            
            entered_at = current_time
            
            if not is_final:
                days = random.randint(2, 7)
                exited_at = current_time + timedelta(days=days)
                outcome = "Passed"
                dropoff = False
                reason = None
            else:
                # Final stage logic
                if stage_idx >= 7:  # Offer or later
                    outcome = random.choices(["Passed", "Passed", "Failed"], weights=[70, 20, 10])[0]
                else:
                    outcome = random.choices(["Passed", "Failed", "Withdrew"], weights=[60, 25, 15])[0]
                
                if outcome == "Passed":
                    exited_at = current_time + timedelta(days=random.randint(1, 5))
                    dropoff = False
                    reason = None
                else:
                    exited_at = current_time + timedelta(days=random.randint(1, 3))
                    dropoff = True
                    reason = random.choice(["Tech Mismatch", "Salary", "Withdrew", "No Response"])
            
            # Store the final stage data for this application (for offers/onboarding)
            if is_final:
                final_stage_per_app[app["application_id"]] = {
                    "final_stage": stage_name,
                    "final_outcome": outcome if is_final else None,
                    "final_exited_at": exited_at,
                    "dropoff_flag": dropoff,
                    "dropoff_reason": reason
                }
                last_exited_at = exited_at
                last_stage_outcome = outcome

            # Create the stage event record
            stage_events.append({
                "stage_event_id": f"EVT-{event_id:06d}",
                "application_id": app["application_id"],
                "stage_name": stage_name,
                "entered_at": entered_at.isoformat(),
                "exited_at": exited_at.isoformat() if exited_at else None,
                "stage_outcome": outcome if is_final else "Passed",
                "dropoff_flag": dropoff,
                "dropoff_reason": reason
            })
            event_id += 1
            
            if exited_at:
                current_time = exited_at + timedelta(hours=random.randint(1, 48))
    
    return stage_events, final_stage_per_app

def generate_interviews(applications, final_stage_per_app):
    """Generates interviews for applications that reached the interview stages."""
    interviews = []
    interview_id = 1
    for app in applications:
        app_id = app["application_id"]
        # Only generate interviews if they reached at least "Screening" (index 1)
        if app_id in final_stage_per_app:
            stage_name = final_stage_per_app[app_id]["final_stage"]
            # Map stage names to interview types
            if stage_name in ["Screening", "Recruiter Screen"]:
                num_interviews = 1
            elif stage_name in ["Technical Interview", "Final Interview"]:
                num_interviews = random.randint(1, 2)
            else:
                num_interviews = 0
            
            for _ in range(num_interviews):
                scheduled = fake.date_time_between(start_date="-60d", end_date="now")
                completed = scheduled + timedelta(hours=random.randint(1, 48))
                interviews.append({
                    "interview_id": f"INT-{interview_id:05d}",
                    "application_id": app_id,
                    "candidate_id": app["candidate_id"],
                    "interview_type": random.choice(INTERVIEW_TYPES),
                    "scheduled_at": scheduled.isoformat(),
                    "completed_at": completed.isoformat() if random.random() > 0.2 else None,
                    "interview_status": random.choice(["Scheduled", "Completed", "Cancelled"]),
                    "technical_score": round(random.uniform(1, 5), 1) if random.random() > 0.3 else None,
                    "communication_score": round(random.uniform(1, 5), 1) if random.random() > 0.3 else None,
                    "overall_score": round(random.uniform(1, 5), 1) if random.random() > 0.3 else None,
                    "recommendation": random.choice(["Strong Hire", "Hire", "No Hire", "Leaning No"]),
                    "feedback": fake.sentence() if random.random() > 0.4 else None
                })
                interview_id += 1
    return interviews

def generate_offers(applications, final_stage_per_app):
    """Generates offers only for applications that reached the 'Offer' stage and passed."""
    offers = []
    offer_id = 1
    for app in applications:
        app_id = app["application_id"]
        if app_id in final_stage_per_app:
            stage = final_stage_per_app[app_id]
            if stage["final_stage"] in ["Offer", "Offer Accepted", "Joined"] and stage["final_outcome"] == "Passed":
                offer_date = stage["final_exited_at"] - timedelta(days=random.randint(1, 5))
                offers.append({
                    "offer_id": f"OFF-{offer_id:05d}",
                    "application_id": app_id,
                    "candidate_id": app["candidate_id"],
                    "offer_date": offer_date.date().isoformat(),
                    "offered_role": random.choice(["Senior Engineer", "Sales Rep", "Product Manager"]),
                    "offered_salary": random.randint(60000, 150000),
                    "currency": "USD",
                    "joining_date": (offer_date + timedelta(days=random.randint(14, 30))).date().isoformat(),
                    "offer_status": random.choice(OFFER_STATUSES),
                    "response_date": (offer_date + timedelta(days=random.randint(2, 7))).date().isoformat() if random.random() > 0.3 else None,
                    "offer_rejection_reason": "Salary Negotiation" if random.random() > 0.7 else None
                })
                offer_id += 1
    return offers

def generate_onboarding(offers):
    """Generates onboarding records only for offers that were accepted."""
    onboarding = []
    onboarding_id = 1
    for offer in offers:
        if offer["offer_status"] == "Accepted":
            planned = datetime.strptime(offer["joining_date"], "%Y-%m-%d")
            actual = planned + timedelta(days=random.randint(-2, 5))
            onboarding.append({
                "onboarding_id": f"ONB-{onboarding_id:05d}",
                "offer_id": offer["offer_id"],
                "application_id": offer["application_id"],
                "candidate_id": offer["candidate_id"],
                "planned_joining_date": planned.date().isoformat(),
                "actual_joining_date": actual.date().isoformat() if random.random() > 0.2 else None,
                "joining_status": random.choice(JOINING_STATUSES),
                "no_join_reason": "Found other offer" if random.random() > 0.8 else None,
                "onboarding_completed": random.choice([True, False])
            })
            onboarding_id += 1
    return onboarding

# --- 3. WRITE CSVs ---
def write_csv(filename, headers, rows):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    print("🚀 Generating FULL Clean Dataset (7 files)...")
    
    candidates = generate_candidates(NUM_CANDIDATES)
    jobs = generate_jobs(NUM_JOBS)
    applications = generate_applications(candidates, jobs, NUM_APPLICATIONS)
    stage_events, final_stage_per_app = generate_stage_events(applications)
    interviews = generate_interviews(applications, final_stage_per_app)
    offers = generate_offers(applications, final_stage_per_app)
    onboarding = generate_onboarding(offers)
    
    write_csv("candidates.csv", ["candidate_id", "email", "first_name", "last_name", "phone"], candidates)
    write_csv("jobs.csv", ["job_id", "job_title", "department", "location", "employment_type"], jobs)
    write_csv("applications.csv", ["application_id", "candidate_id", "job_id", "application_date", "source"], applications)
    write_csv("stage_events.csv", ["stage_event_id", "application_id", "stage_name", "entered_at", "exited_at", "stage_outcome", "dropoff_flag", "dropoff_reason"], stage_events)
    write_csv("interviews.csv", ["interview_id", "application_id", "candidate_id", "interview_type", "scheduled_at", "completed_at", "interview_status", "technical_score", "communication_score", "overall_score", "recommendation", "feedback"], interviews)
    write_csv("offers.csv", ["offer_id", "application_id", "candidate_id", "offer_date", "offered_role", "offered_salary", "currency", "joining_date", "offer_status", "response_date", "offer_rejection_reason"], offers)
    write_csv("onboarding.csv", ["onboarding_id", "offer_id", "application_id", "candidate_id", "planned_joining_date", "actual_joining_date", "joining_status", "no_join_reason", "onboarding_completed"], onboarding)
    
    print("🎉 Full clean dataset generated!")