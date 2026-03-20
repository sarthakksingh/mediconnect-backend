import requests
import os
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL_APPOINTMENT = os.getenv("N8N_WEBHOOK_URL_APPOINTMENT")
N8N_WEBHOOK_URL_REPORT = os.getenv("N8N_WEBHOOK_URL_REPORT")


def trigger_agent(payload: dict):
    """
    Routes event to the correct n8n webhook based on event type.

    APPOINTMENT_CREATED     → Appointment Reminder workflow
    APPOINTMENT_RESCHEDULED → Appointment Reminder workflow
    REPORT_READY            → Report Notification workflow
    """
    event_type = payload.get("type")

    # Route to correct webhook
    if event_type in ["APPOINTMENT_CREATED", "APPOINTMENT_RESCHEDULED"]:
        url = N8N_WEBHOOK_URL_APPOINTMENT
    elif event_type == "REPORT_READY":
        url = N8N_WEBHOOK_URL_REPORT
    else:
        print(f"⚠️ Unknown event type: {event_type}")
        return

    if not url:
        print(f"⚠️ Webhook URL not set for event type: {event_type}")
        return

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"✅ Agent triggered for {event_type} → Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Agent webhook failed for {event_type}: {e}")