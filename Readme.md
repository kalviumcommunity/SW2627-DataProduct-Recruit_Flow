# Sales Analytics & RecruitFlow Dashboard

Interactive analytics dashboard that ingests sales data, computes KPIs, detects threshold breaches, and delivers weekly reports. Built for operations, HR, and sales teams.

---

## Getting Started

Run the project in 4 simple commands:

```bash
git clone https://github.com/kalviumcommunity/SW2627-DataProduct-Recruit_Flow.git
cd SW2627-DataProduct-Recruit_Flow
pip install -r requirements.txt
streamlit run app.py
```

---

## Dataset

- **Source**: CSV upload or scheduled pipeline ingestion
- **Columns**: `customer_id`, `order_id`, `amount`, `date`, `segment` (also supports `revenue`, `churn`, `nps` columns)
- **Refresh**: Weekly via GitHub Actions pipeline

---

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kalviumcommunity/SW2627-DataProduct-Recruit_Flow.git
   cd SW2627-DataProduct-Recruit_Flow
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your SMTP credentials
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## Usage

- Upload a CSV file via the sidebar or let the automated pipeline load data automatically.
- Use sidebar filters (Date Range, Segments, Revenue Range) to explore metrics.
- Check real-time KPI cards for status overview.
- Review visual alerts (`st.error` / `st.warning`) for threshold breaches.
- Generate structured summary reports and send them via email.

---

## Pipeline Architecture

```text
CSV Upload / Scheduled Ingest
        |
    Ingestion: Load raw CSV, validate file format
        |
    Cleaning: Drop nulls, cast types, filter invalid rows
        |
    Aggregation: Group by segment, compute revenue and order count
        |
    Output: Write cleaned.csv and aggregated.csv to output/
        |
    Dashboard: Load processed data, compute KPIs, render charts
        |
    Alerts: Check metrics against thresholds, display warnings
        |
    Reports: Generate summary, send via email
```

---

## Derived Features

| Column           | Type    | Description                          | Example  |
|------------------|---------|--------------------------------------|----------|
| `revenue_30d`      | float   | Sum of order amounts last 30 days    | 4523.50  |
| `days_since_order` | integer | Days since most recent order         | 12       |
| `churn_risk`       | string  | Risk category based on activity      | "high"   |
| `null_pct`         | float   | Percentage of null values per column | 2.3      |

---

## Known Limitations

- Data refreshes weekly. Dashboard does not show real-time streaming data.
- Revenue excludes refunded orders.
- Segment classification based on self-reported category field.
- Alert thresholds are static (no seasonal adjustment).
- Email delivery requires SMTP configuration in `.env` file.
- Pipeline assumes CSV with specific column names (`customer_id`, `order_id`, `amount`, `date`, `segment`).

---

## 🏗️ Project Components & Architecture

### Streamlit & Python Data Pipeline
- `app.py`: Main interactive Streamlit application (KPI dashboard, multi-step workflow, charts, explorer, and email report UI).
- `pipeline.py`: Automated ingestion, cleaning, aggregation, and output pipeline.
- `alert_config.py`: Threshold configuration dictionary for business metrics monitoring.
- `report_generator.py`: Generates structured text summary reports.
- `email_sender.py`: Delivers summary reports via SMTP with non-blocking error handling.
- `validate_data.py`: Data quality and schema validation script.
- `.github/workflows/pipeline.yml`: GitHub Actions schedule for weekly pipeline execution.
- `.github/workflows/validate.yml`: GitHub Actions CI workflow for data schema validation on push/PR.

### Enterprise Web Application (FastAPI & Next.js)
- `backend/`: FastAPI backend with SQLAlchemy, Pydantic schemas, and analytics engine.
- `frontend/`: Next.js 14 App Router frontend with Tailwind CSS and interactive dashboard components.
