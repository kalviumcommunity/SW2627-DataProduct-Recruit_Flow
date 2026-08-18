# RecruitFlow Data Model

This document defines the canonical data contract for the MVP recruitment intelligence pipeline.

It is the source of truth for:
- database schema work
- ingestion validation
- cleaning and normalization
- journey reconstruction
- analytics endpoints

The goal is to support one core business question:

> Where are candidates dropping off, which departments are affected, and why?

## Entity Strategy

RecruitFlow uses two modeling layers:

- **Operational entities**: the raw business records we ingest and normalize
- **Analytical journey entities**: the reconstructed stage timeline used for funnel analysis

The current MVP centers on four operational entities:

- `candidates`
- `jobs`
- `applications`
- `stage_events`

For the next phase of the MVP, we also define supporting entities:

- `interviews`
- `offers`
- `onboarding`

These supporting entities are important for a full recruitment story, but they are not yet fully wired through the ingestion pipeline. This document defines the contract so the rest of the implementation can follow one clear model.

## Canonical Principles

- Keep `core` tables as the trusted, deduplicated business truth.
- Keep `staging` tables nullable and tolerant of incomplete source data.
- Preserve raw source values where possible.
- Normalize values during cleaning, not during parsing.
- Store provenance fields so we can always trace a row back to its source upload.
- Model journey reconstruction as an analytical view over canonical events.

## Shared Fields

Most entities share a common audit and lineage pattern.

### Common lineage fields

- `ingestion_batch_id`: UUID of the upload batch that introduced the row
- `source_row_number`: original row number in the uploaded file
- `raw_record_id`: reference back to `raw.raw_records.id`
- `created_at`: timestamp when the row was created in the pipeline

### Common pipeline state fields

- `validation_status`: `pending`, `valid`, `warning`, `error`
- `validation_error_count`: number of validation issues found
- `cleaned_status`: `pending`, `cleaned`, `review`
- `cleaned_at`: timestamp when cleaning finished

## 1. Candidate

### Business meaning

Represents one real person in the recruitment system.

### Canonical key

- `candidate_id`

### Core fields

- `candidate_id`
- `email`
- `original_email`
- `first_name`
- `last_name`
- `phone`

### Supporting fields

- `department`  
  This is usually derived from the job/application context, not stored directly as the primary candidate identity.
- `job_role`  
  This is typically inferred from the linked job.
- `application_date`  
  This belongs to the application record, not the candidate record.

### Validation rules

- `candidate_id` is required.
- Email should be trimmed and normalized to lowercase.
- Phone should preserve a human-readable canonical form.

### Cleaning rules

- Normalize whitespace.
- Lowercase email.
- Preserve original email in `original_email`.

## 2. Job

### Business meaning

Represents an open role or requisition.

### Canonical key

- `job_id`

### Core fields

- `job_id`
- `job_title`
- `department_id`

### Staging fields

- `department`
- `location`
- `employment_type`

### Validation rules

- `job_id`, `job_title`, and `department` are required.
- Department must map to a canonical department.

### Cleaning rules

- Normalize department aliases to canonical department names.
- Preserve raw department text if needed for audit/review.

## 3. Application

### Business meaning

Represents a candidate applying for a job.

### Canonical key

- `application_id`

### Core fields

- `application_id`
- `candidate_id` foreign key to `core.candidates.id`
- `job_id` foreign key to `core.jobs.id`
- `application_date`
- `source`

### Validation rules

- `application_id`, `candidate_id`, `job_id`, and `application_date` are required.
- `application_date` must parse as a valid date.
- The linked candidate and job must exist by the time the row is resolved into core.

### Cleaning rules

- Standardize date format.
- Trim and normalize source values.

## 4. Recruitment Stage Event

### Business meaning

Represents a candidate moving through a recruitment stage.

### Canonical key

- `stage_event_id`

### Core fields

- `stage_event_id`
- `application_id`
- `stage_id`
- `entered_at`
- `exited_at`
- `dropoff_flag`
- `dropoff_reason`
- `feedback`

### Analytical fields

- `stage_outcome`
- `is_derived`
- `derivation_reason`

### Validation rules

- `stage_event_id`, `application_id`, `stage_name`, and `entered_at` are required.
- `entered_at` must parse as a valid timestamp.
- `exited_at` is optional but must parse if present.
- `dropoff_flag` must be boolean-compatible.
- `dropoff_reason` is required if `dropoff_flag = true`.

### Cleaning rules

- Normalize stage names to canonical stage names.
- Standardize timestamps.
- Normalize boolean values.
- Normalize drop-off reasons where possible.

## 5. Interview

### Business meaning

Represents one interview instance connected to an application.

### Canonical key

- `interview_id`

### Recommended staging fields

- `interview_id`
- `application_id`
- `candidate_id`
- `interview_type`
- `scheduled_at`
- `completed_at`
- `interview_status`
- `technical_score`
- `communication_score`
- `overall_score`
- `recommendation`
- `feedback`

### Recommended core modeling approach

For the MVP, interviews should be modeled as a first-class supporting entity if the business wants interview-specific analytics.

If the MVP keeps the focus on funnel bottlenecks, interviews can also be treated as an analytical supporting table that enriches the candidate journey without replacing `stage_events`.

### Validation rules

- `interview_id` and `application_id` are required.
- `scheduled_at` should parse as a timestamp if present.
- `completed_at` should parse as a timestamp if present.
- Scores should be numeric and bounded to the chosen scale.

### Cleaning rules

- Normalize interview type labels.
- Normalize interview status labels.
- Convert timestamps to canonical format.

## 6. Offer

### Business meaning

Represents an offer extended to a candidate.

### Canonical key

- `offer_id`

### Recommended staging fields

- `offer_id`
- `application_id`
- `candidate_id`
- `offer_date`
- `offered_role`
- `offered_salary`
- `currency`
- `joining_date`
- `offer_status`
- `response_date`
- `offer_rejection_reason`

### Recommended core modeling approach

Offers should be represented in a way that supports:
- offer acceptance rate
- offer decline reasons
- time from offer to joining

### Validation rules

- `offer_id` and `application_id` are required.
- `offer_date` should parse as a date.
- `offered_salary` should be numeric if present.
- `offer_status` should be constrained to the canonical status list.

### Cleaning rules

- Standardize status values.
- Normalize currency and salary formatting.
- Normalize rejection reasons.

## 7. Onboarding

### Business meaning

Represents the final joiner/onboarding outcome after an accepted offer.

### Canonical key

- `onboarding_id`

### Recommended staging fields

- `onboarding_id`
- `offer_id`
- `application_id`
- `candidate_id`
- `planned_joining_date`
- `actual_joining_date`
- `joining_status`
- `no_join_reason`
- `onboarding_completed`

### Recommended core modeling approach

Onboarding supports the final funnel metrics:
- joining rate
- no-show rate
- onboarding completion

### Validation rules

- `onboarding_id` and `application_id` are required.
- `planned_joining_date` should parse as a date if present.
- `actual_joining_date` should parse as a date if present.
- `joining_status` should map to a canonical set.

### Cleaning rules

- Normalize join status labels.
- Standardize date formats.
- Normalize no-join reasons.

## Canonical Reference Lists

### Departments

- Engineering
- Sales
- Marketing
- IT
- HR
- Finance

### Stages

- Applied
- Screening
- Recruiter Screen
- Hiring Manager Review
- Technical Interview
- Final Interview
- Offer
- Offer Accepted
- Joined

### Offer statuses

- Sent
- Accepted
- Declined
- Expired

### Joining statuses

- Joined
- No Show
- Postponed
- Cancelled

### Interview status examples

- Scheduled
- Completed
- Cancelled

### Interview recommendations

- Strong Hire
- Hire
- Leaning No
- No Hire

## Relationship Model

- One `candidate` can have many `applications`
- One `job` can have many `applications`
- One `application` can have many `stage_events`
- One `application` can have many `interviews`
- One `application` can have at most one winning `offer` in the ideal MVP flow, but the schema should not assume that until business rules are finalized
- One `offer` can have one `onboarding` record

## What Counts as MVP-Complete

The MVP is complete when the system can:

- ingest the main recruitment files
- validate and clean them
- reconstruct the recruitment journey
- identify where candidates drop off
- show bottlenecks by department and role
- explain drop-offs using structured reasons
- expose the results through the API

## Notes For Future Implementation

- Interviews, offers, and onboarding are defined here first so schema and code changes can follow one stable contract.
- If a field is not yet supported in the current pipeline, it should be added to staging first.
- Only promote a field into core when it is needed for deduplicated business truth or downstream analytics.

