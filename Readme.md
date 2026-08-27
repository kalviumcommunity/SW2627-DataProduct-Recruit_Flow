# 🎯 RecruitFlow - HR Recruitment Intelligence Platform

> An enterprise HR analytics and recruitment intelligence platform that consolidates multi-source hiring data into a unified data layer and transforms it into actionable funnel insights.

---

## 📌 1. The Core Problem Statement

HR teams have recruitment funnel data, interview feedback, and onboarding records, but **no shared reporting system** identifies which hiring stages contribute most to candidate drop-offs across departments.

### Why This Is a Critical Problem
The problem is **not that data doesn't exist**—the problem is that it lives in **disconnected silos**:
* **Recruitment / ATS:** Tracks candidate details, application dates, departments, and basic status.
* **Interview Records:** Tracks technical scores, communication scores, recommendations, and rejection reasons.
* **Onboarding / HRIS:** Tracks offer acceptance, joining dates, actual join status, and dropouts.

Without connecting these systems into a single candidate journey, company-wide averages mask deep, department-specific bottlenecks:
* An overall **20% interview drop-off** might hide a **45% failure rate in IT technical rounds** (due to mismatch in assessment level) vs. a **30% loss in Sales at the offer stage** (due to compensation expectations).

---

## 💡 2. The Solution & Value Proposition

**RecruitFlow** acts as a centralized **Talent Command Center** that:
1. **Unifies Multi-Source HR Data:** Ingests and standardizes records across 5 core datasets using `candidate_id` as the canonical join key.
2. **Reconstructs Candidate Journeys:** Maps the chronological progression from initial application through interviews, offers, and verified onboarding.
3. **Identifies Stage Bottlenecks:** Calculates stage-to-stage conversion rates, drop-off percentages, and time-in-stage delays.
4. **Uncovers the "Why":** Correlates drop-offs with structured exit reasons (Technical Skill Mismatch, Salary Expectations, Process Delay, Candidate Withdrew).
5. **Enables Department & Role Drill-Down:** Allows HR leaders to filter by department, job role, and date range in sub-second queries.
6. **Passes the "30-Second Test":** Enables any stakeholder to identify the single biggest hiring bottleneck and its root cause within 30 seconds.

---

## 🏗️ 3. Architecture & Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Next.js Web Frontend                          │
│        (Next.js 14 App Router, React 18, Tailwind CSS, Lucide React)    │
│           • /dashboard  (KPIs, Funnel, Department & Reason Charts)      │
│           • /upload     (Batch Selection: New, Append, Clear + DnD)     │
│           • /login & /signup (HR Authentication)                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API (JSON / JWT)
┌────────────────────────────────────▼────────────────────────────────────┐
│                           FastAPI Backend                               │
│           (Python 3.11+, Pydantic v2, SQLAlchemy 2.0, Pandas)           │
│           • Auth Service (bcrypt hashing, JWT tokens)                   │
│           • Batch Management API (New, Append, Clear)                   │
│           • Ingestion & Normalization Layer (Validation & Cleaning)     │
│           • Journey Reconstruction & Funnel Analytics Engine            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ SQL (psycopg2 / SQLAlchemy)
┌────────────────────────────────────▼────────────────────────────────────┐
│                         PostgreSQL Data Store                           │
│           • staging schema (tolerant ingestion & audit lineage)         │
│           • core schema (canonical deduplicated truth)                  │
│           • analytical views (v_candidate_journey, funnel rollups)      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. Canonical Data Model & Ingestion Datasets

RecruitFlow links 5 primary entity datasets and 2 reference master tables via `candidate_id`:

```
                    ┌─────────────────────────┐
                    │     candidates.csv      │
                    │      (Master Profile)   │
                    └────────────┬────────────┘
                                 │ candidate_id
        ┌────────────────────────┼────────────────────────┐
        ↓                        ↓                        ↓
┌───────────────────────┐ ┌─────────────┐ ┌───────────────────────┐
│ recruitment_stages.csv│ │interviews.csv│ │      offers.csv       │
│     (Funnel Events)   │ │  (Feedback) │ │   (Offer & Comp)      │
└───────────┬───────────┘ └──────┬──────┘ └───────────┬───────────┘
            └────────────────────┼────────────────────┘
                                 ↓ candidate_id
                        ┌─────────────────┐
                        │ onboarding.csv  │
                        │ (Join Outcome)  │
                        └─────────────────┘
```

### The 5 Core Datasets & Master References

| Dataset | Key Columns | Business Purpose |
| :--- | :--- | :--- |
| **`candidates.csv`** | `candidate_id`, `department`, `job_role`, `location`, `experience_level`, `application_date`, `source` | Master profile establishing hiring context. |
| **`recruitment_stages.csv`** | `candidate_id`, `stage`, `entered_at`, `exited_at`, `status`, `exit_reason` | Temporal tracking of candidate movement through stages. |
| **`interviews.csv`** | `interview_id`, `candidate_id`, `interview_stage`, `score`, `recommendation`, `feedback`, `rejection_reason` | Assessment scores and specific interviewer feedback. |
| **`offers.csv`** | `offer_id`, `candidate_id`, `offer_date`, `offered_role`, `offered_salary`, `offer_status`, `acceptance_date` | Compensation package tracking and offer acceptance rates. |
| **`onboarding.csv`** | `candidate_id`, `planned_joining_date`, `actual_joining_date`, `joining_status`, `onboarding_status` | Verifies whether accepted offers converted into actual joiners. |
| **`stage_master.csv`** | `stage_code`, `stage_name`, `stage_order` (1: Applied → 8: Joined) | Standardizes stage sequence and aliases across ATS sources. |
| **`reason_master.csv`**| `reason_code`, `reason_category` (Tech Mismatch, Salary, Role Mismatch, Withdrawal, Delay) | Normalizes rejection reasons into structured categories. |

---

## 📈 5. The Hiring Funnel Pipeline

```text
  [1] Application (10,000)
         ↓  (20% drop)
  [2] Screening (8,000)
         ↓  (15% drop)
  [3] Interview (6,800)
         ↓  (45% drop 🔴 Technical Bottleneck in IT)
  [4] Technical / Department Round (3,740)
         ↓  (15% drop)
  [5] HR Round (3,179)
         ↓  (30% drop 🟠 Offer Bottleneck in Sales)
  [6] Offer Extended (2,225)
         ↓  (15% drop)
  [7] Offer Accepted (1,891)
         ↓  (10% drop / no-shows)
  [8] Joined & Onboarded (1,702)
```

---

## 📁 6. Repository Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes (auth, batches, ingestion, analytics)
│   │   ├── core/                # Database configuration & settings
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Ingestion, validation, journey reconstruction & analytics
│   │   └── main.py              # Application entry point
│   ├── migrations/              # PostgreSQL DDL migrations (001 to 007)
│   ├── scripts/                 # Synthetic data generation & scale datasets
│   ├── Dockerfile               # Backend container configuration
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── app/                     # Next.js 14 App Router
│   │   ├── dashboard/           # Analytics command center & visual funnel
│   │   ├── upload/              # Batch management & file ingestion UI
│   │   ├── login/               # HR Authentication
│   │   ├── signup/              # Account registration
│   │   ├── globals.css          # Tailwind styling
│   │   └── layout.jsx           # Root layout wrapper
│   ├── components/              # Modular UI, Dashboard & Upload dropzone components
│   ├── src/                     # Shared components, analytics utils & mock data
│   ├── lib/                     # Client helper libraries
│   ├── package.json             # Node dependencies
│   ├── tailwind.config.js       # Design tokens & dark mode configuration
│   └── postcss.config.js        # PostCSS configuration
├── docs/
│   └── data-model.md            # Canonical data model specification
├── docker-compose.yml           # Multi-container orchestration (DB + API + Web)
├── expected_results.json        # Test validation benchmarks
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git exclusion rules
└── Readme.md                    # Canonical project documentation
```

---

## ⚡ 7. Running the Project Locally

### Option A: Using Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/kalviumcommunity/SW2627-DataProduct-Recruit_Flow.git
cd SW2627-DataProduct-Recruit_Flow

# 2. Setup environment variables
cp .env.example .env

# 3. Start PostgreSQL, FastAPI Backend, and Next.js Frontend
docker-compose up --build
```
* **Frontend Web Dashboard:** `http://localhost:3000`
* **FastAPI Interactive Docs (Swagger):** `http://localhost:8000/docs`
* **PostgreSQL Database:** `localhost:5432`

---

### Option B: Running Services Individually

#### 1. Backend Service
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/recruitflow"
export SECRET_KEY="your-secret-key"

# Initialize Database & Start Server
python create_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 🌐 8. Core API Endpoints

### 🔐 Authentication
* `POST /api/auth/signup`: Register a new HR user.
* `POST /api/auth/login`: Authenticate and receive a JWT bearer token.

### 📦 Batch Management
* `GET /api/batches`: List all uploaded recruitment batches.
* `POST /api/batches/new`: Create a new isolated batch for fresh data.
* `POST /api/batches/{id}/append`: Append incremental data to an existing batch.
* `DELETE /api/batches/{id}`: Purge a batch and reset associated analytics.

### 📊 Analytics & Insights
* `GET /api/v1/analytics/funnel`: Aggregate funnel conversion and stage drop-offs.
* `GET /api/v1/analytics/bottlenecks`: Average and median days spent per stage.
* `GET /api/v1/analytics/dropoff-reasons`: Top rejection/exit reasons grouped by stage and department.
* `GET /api/v1/analytics/department-comparison`: Comparative metrics across IT, Sales, Finance, etc.

---

## 👥 9. Team Collaboration & Milestone Ownership

| Teammate | Focus Area | Key Deliverables |
| :--- | :--- | :--- |
| **Teammate A** | **Data & Ingestion** | Schema Design, Migrations, Sample Datasets, CSV/Excel Upload, Validation & Normalization Layer, Journey Join Logic. |
| **Teammate B** | **Backend & Analytics** | FastAPI Scaffold, Journey Query Service, Funnel Metrics Engine, Time-at-Stage, Filter APIs, Reason Aggregation, Auth. |
| **Teammate C** | **Frontend & Dashboard** | Next.js Dashboard UI, Visual Funnel Charts, Filter Controls, Batch Upload UI, 30-Second MVP Validation, Polish. |
