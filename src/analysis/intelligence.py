import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_FEATURES = os.path.join(BASE_DIR, "data", "processed", "candidate_features.csv")
SRC_STAGES = os.path.join(BASE_DIR, "data", "processed", "stage_duration_summary.json")
SRC_DEPTS = os.path.join(BASE_DIR, "data", "processed", "department_analysis_summary.json")
SRC_REASONS = os.path.join(BASE_DIR, "data", "processed", "reasons_analysis_summary.json")
DEST_DIR = os.path.join(BASE_DIR, "data", "processed")

def generate_hr_intelligence():
    print("="*60)
    print(" STARTING AUTOMATED HR INTELLIGENCE & RECOMMENDATION ENGINE")
    print("="*60)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    if not os.path.exists(SRC_FEATURES):
        print(f"Error: {SRC_FEATURES} not found.")
        return
        
    df_features = pd.read_csv(SRC_FEATURES)
    
    detected_anomalies = []
    recommendations = []
    
    # 1. Detect Stage Duration & Bottleneck Spikes (>= +15% above average stage duration benchmark)
    # Calculate baseline average stage duration across all pipeline stages
    stage_dur_cols = [c for c in df_features.columns if c.startswith('duration_') and c.endswith('_days')]
    stage_means = {col.replace('duration_', '').replace('_days', '').capitalize(): df_features[col].mean() for col in stage_dur_cols}
    overall_avg_stage_dur = np.mean(list(stage_means.values())) if stage_means else 3.0
    
    for stage_name, avg_dur in stage_means.items():
        pct_diff = ((avg_dur - overall_avg_stage_dur) / overall_avg_stage_dur) * 100.0 if overall_avg_stage_dur > 0 else 0.0
        if pct_diff >= 15.0:
            anomaly = {
                "type": "STAGE_DURATION_SPIKE",
                "target": stage_name,
                "metric": "avg_duration_days",
                "value": round(avg_dur, 2),
                "benchmark": round(overall_avg_stage_dur, 2),
                "percentage_above_benchmark": round(pct_diff, 1)
            }
            detected_anomalies.append(anomaly)
            
            if stage_name.lower() in ["joined", "offer"]:
                recommendations.append({
                    "id": f"REC-STAGE-{stage_name.upper()}",
                    "priority": "HIGH",
                    "category": "Pipeline Velocity",
                    "target_stage": stage_name,
                    "target_department": "All",
                    "issue": f"{stage_name} stage duration ({avg_dur:.1f} days) is {pct_diff:.1f}% above the pipeline benchmark ({overall_avg_stage_dur:.1f} days).",
                    "recommended_action": f"Streamline onboarding documentation and implement weekly pre-joining touchpoints during notice period to compress {stage_name} turnaround time.",
                    "expected_impact": "Reduce total recruitment cycle time by 30-40% and prevent candidate ghosting."
                })
                
    # 2. Detect Department Drop-off Spikes (>= +15% delta above company average)
    company_dropped = df_features['dropped'].sum()
    company_total = len(df_features)
    company_drop_rate = (company_dropped / company_total) * 100.0 if company_total > 0 else 0.0
    
    for dept_name, group in df_features.groupby('department'):
        dept_total = len(group)
        dept_dropped = group['dropped'].sum()
        dept_rate = (dept_dropped / dept_total) * 100.0 if dept_total > 0 else 0.0
        delta = dept_rate - company_drop_rate
        
        if delta >= 15.0:
            detected_anomalies.append({
                "type": "DEPARTMENT_DROPOFF_SPIKE",
                "target": dept_name,
                "metric": "dropoff_rate",
                "value": round(dept_rate, 2),
                "benchmark": round(company_drop_rate, 2),
                "percentage_above_benchmark": round(delta, 1)
            })
            
            recommendations.append({
                "id": f"REC-DEPT-{dept_name.upper()}",
                "priority": "HIGH",
                "category": "Department Attrition",
                "target_stage": "Multiple",
                "target_department": dept_name,
                "issue": f"{dept_name} department drop-off rate ({dept_rate:.1f}%) exceeds company average ({company_drop_rate:.1f}%) by +{delta:.1f}%.",
                "recommended_action": f"Conduct an audit of {dept_name} interview criteria, compensation benchmarking, and role expectations with department hiring managers.",
                "expected_impact": "Improve departmental offer acceptance and conversion rates by 20-25%."
            })
            
    # 3. Detect Top Rejection Reason Friction (e.g. Technical Mismatch >= 25% or >= +15% above 10% baseline)
    dropped_candidates = df_features[df_features['dropped'] == 1]
    if not dropped_candidates.empty:
        reason_counts = dropped_candidates['rejection_reason'].value_counts()
        total_drops = len(dropped_candidates)
        baseline_reason_pct = 10.0
        
        for reason, count in reason_counts.items():
            reason_pct = (count / total_drops) * 100.0
            if reason_pct >= 25.0:
                pct_above = round(((reason_pct - baseline_reason_pct) / baseline_reason_pct) * 100.0, 1)
                detected_anomalies.append({
                    "type": "REJECTION_REASON_CLUSTER",
                    "target": str(reason),
                    "metric": "reason_percentage",
                    "value": round(reason_pct, 1),
                    "benchmark": baseline_reason_pct,
                    "percentage_above_benchmark": pct_above
                })

                
                if "technical" in str(reason).lower():
                    recommendations.append({
                        "id": "REC-SCREENING-TECH-MISMATCH",
                        "priority": "HIGH",
                        "category": "Candidate Quality & Screening",
                        "target_stage": "Screening & Technical Interview",
                        "target_department": "IT / Engineering",
                        "issue": f"'{reason}' accounts for {reason_pct:.1f}% of total candidate drop-offs.",
                        "recommended_action": "Introduce automated coding pre-assessments and stricter resume keyword screening before scheduling live technical rounds.",
                        "expected_impact": "Save 15+ engineering interview hours per week and increase interview pass-through rate."
                    })
                elif "no show" in str(reason).lower():
                    recommendations.append({
                        "id": "REC-ONBOARDING-NO-SHOW",
                        "priority": "MEDIUM",
                        "category": "Candidate Engagement",
                        "target_stage": "Joined",
                        "target_department": "All",
                        "issue": f"No-show drop-offs represent {reason_pct:.1f}% of candidate loss at the joining stage.",
                        "recommended_action": "Establish an automated SMS/WhatsApp reminder system and assign a buddy mentor before day 1.",
                        "expected_impact": "Reduce day-1 no-shows to under 5%."
                    })
                    
    # 4. Detect Delayed Drop-offs (High candidate pipeline waste)
    delayed_drops = df_features[df_features['is_delayed_dropoff'] == 1] if 'is_delayed_dropoff' in df_features.columns else pd.DataFrame()
    if len(delayed_drops) > 0:
        detected_anomalies.append({
            "type": "DELAYED_DROPOFF_INEFFICIENCY",
            "target": "Pipeline SLA",
            "metric": "delayed_dropoffs_count",
            "value": len(delayed_drops),
            "benchmark": 0,
            "percentage_above_benchmark": 100.0
        })
        recommendations.append({
            "id": "REC-SLA-DELAYED-DROPOFFS",
            "priority": "MEDIUM",
            "category": "Process Governance",
            "target_stage": "Interview",
            "target_department": "All",
            "issue": f"{len(delayed_drops)} candidates spent significantly above-median time in interview stages before ultimately being rejected.",
            "recommended_action": "Enforce a strict 5-day SLA from final round interview to hiring manager feedback decision.",
            "expected_impact": "Eliminate candidate frustration and prevent prolonged interview latency."
        })
        
    df_recs = pd.DataFrame(recommendations)
    
    # Save CSV & JSON
    dest_csv = os.path.join(DEST_DIR, "hr_intelligence_recommendations.csv")
    df_recs.to_csv(dest_csv, index=False)
    
    full_payload = {
        "anomalies_detected": detected_anomalies,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations
    }
    
    dest_json = os.path.join(DEST_DIR, "hr_intelligence_recommendations.json")
    with open(dest_json, "w") as f:
        json.dump(full_payload, f, indent=2)
        
    print(f" Saved HR Recommendations (CSV): {dest_csv}")
    print(f" Saved HR Recommendations (JSON): {dest_json}\n")
    print("--- Detected Anomalies (Spikes >= +15%) ---")
    for a in detected_anomalies:
        print(f" * [{a['type']}] {a['target']}: Value={a['value']} vs Benchmark={a['benchmark']} (+{a['percentage_above_benchmark']}%)")
        
    print("\n--- Generated Action Recommendations for HR ---")
    print(df_recs[['id', 'priority', 'target_department', 'issue']].to_string(index=False))
    print("\n Automated HR Intelligence & Recommendation Engine Completed Successfully!")

if __name__ == "__main__":
    generate_hr_intelligence()
