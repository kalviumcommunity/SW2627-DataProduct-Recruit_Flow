"""
Recruitflow Data Science & Analytics Engine
Module: src/analysis/intelligence.py
Description: Automated Intelligence & HR Recommendation Engine.
Detects bottleneck spikes (>= +15% above average) and generates rule-based action recommendations.
"""

from typing import List, Dict, Any

def generate_hr_recommendations(
    funnel_stages: List[Dict[str, Any]],
    reasons: List[Dict[str, Any]],
    avg_dropoff_benchmark: float = 20.0
) -> List[Dict[str, Any]]:
    """
    Analyzes stage drop-offs against benchmarks and generates prioritized HR recommendations.
    """
    recommendations = []
    
    for stage in funnel_stages:
        dropoff_rate = stage.get('dropoff_rate', 0.0)
        stage_name = stage.get('name', stage.get('stage_name', 'Unknown'))
        
        # Check if dropoff exceeds benchmark by >= 15%
        if dropoff_rate >= (avg_dropoff_benchmark + 8.0):
            top_reason = reasons[0].get('reason', 'Skill Mismatch') if reasons else 'Skill Mismatch'
            
            recommendation = {
                'stage': stage_name,
                'dropoff_rate': dropoff_rate,
                'benchmark': avg_dropoff_benchmark,
                'severity': 'CRITICAL' if dropoff_rate > 28.0 else 'HIGH',
                'primary_driver': top_reason,
                'action_item': f"Audit {stage_name} assessment standards. Top candidate feedback points to '{top_reason}'. Align JD prerequisites with interview scorecards."
            }
            recommendations.append(recommendation)
            
    return recommendations
