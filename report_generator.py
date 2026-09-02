import pandas as pd

def generate_report(df, report_date):
    """Generate structured text report from analysis output."""
    revenue = float(df["revenue"].sum()) if "revenue" in df.columns else 0.0
    customers = df["customer_id"].nunique() if "customer_id" in df.columns else len(df)
    avg_order = float(df["revenue"].mean()) if "revenue" in df.columns else 0.0

    lines = []
    lines.append("WEEKLY ANALYTICS REPORT")
    lines.append("Date: " + str(report_date))
    lines.append("")
    lines.append("== KPI SUMMARY ==")
    lines.append("Total Revenue: $" + f"{revenue:,.0f}")
    lines.append("Active Customers: " + f"{customers:,}")
    lines.append("Average Order: $" + f"{avg_order:,.0f}")
    lines.append("")
    lines.append("== KEY FINDING ==")
    if "segment" in df.columns and "revenue" in df.columns and len(df) > 0:
        top_seg = str(df.groupby("segment")["revenue"].sum().idxmax())
    else:
        top_seg = "N/A"
    lines.append("Top segment: " + top_seg)
    lines.append("")
    lines.append("== RECOMMENDED ACTION ==")
    lines.append("Allocate resources to high-growth segments.")
    return "\n".join(lines)
