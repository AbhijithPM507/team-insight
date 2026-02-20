import requests
import os


N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", None)


def send_to_n8n(result_json):
    """
    Sends analysis result to n8n webhook if configured.
    """

    if not N8N_WEBHOOK_URL:
        return

    try:
        requests.post(N8N_WEBHOOK_URL, json=result_json)
    except Exception as e:
        print("Failed to send to n8n:", str(e))