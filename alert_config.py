"""
Configuration file storing business metric threshold definitions for visual alerts.
"""

ALERT_THRESHOLDS = {
    "churn_rate": {
        "metric": "Churn Rate",
        "threshold": 7.0,
        "direction": "above",
        "severity": "critical",
        "message": "Churn exceeds safe limit. Investigate retention."
    },
    "avg_order_value": {
        "metric": "Avg Order Value",
        "threshold": 30.0,
        "direction": "below",
        "severity": "warning",
        "message": "AOV below target. Check pricing and product mix."
    },
    "null_percentage": {
        "metric": "Data Quality",
        "threshold": 5.0,
        "direction": "above",
        "severity": "warning",
        "message": "Null percentage too high. Check data pipeline."
    }
}
