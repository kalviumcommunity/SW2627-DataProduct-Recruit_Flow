import os
import smtplib
from email.mime.text import MIMEText

def send_report(report_text, recipient):
    """Send analytics report via email using SMTP environment variable credentials."""
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    if not sender or not password:
        print("Email not configured. Skipping.")
        return False

    msg = MIMEText(report_text)
    msg["Subject"] = "Weekly Analytics Report"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Send failed: " + str(e))
        return False
