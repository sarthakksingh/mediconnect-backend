import requests
import os
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def trigger_agent(payload: dict):
    """
    Sends event payload to n8n agent webhook
    Example:
    Appointment booked → Reminder workflow
    Report ready → Notification workflow
    """
    try:
        requests.post(N8N_WEBHOOK_URL, json=payload)
        print("✅ Agent Triggered Successfully")
    except Exception as e:
        print("⚠️ Agent webhook failed:", e)
