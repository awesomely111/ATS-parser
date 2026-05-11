"""
Email Service Module
"""
import requests
from msal import ConfidentialClientApplication
import os

class OutlookEmailService:
    def __init__(self, client_id=None, client_secret=None, tenant_id=None, outlook_email=None):
        self.client_id = client_id or os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("MICROSOFT_TENANT_ID")
        self.outlook_email = outlook_email or os.getenv("OUTLOOK_EMAIL")
        self.access_token = None

    def authenticate(self):
        try:
            app = ConfidentialClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret,
            )
            result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
        except:
            pass
        return False

    def send_email(self, to_email, subject, body_html):
        if not self.access_token:
            if not self.authenticate():
                return False
        try:
            url = f"https://graph.microsoft.com/v1.0/users/{self.outlook_email}/sendMail"
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            email_data = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": body_html},
                    "toRecipients": [{"emailAddress": {"address": to_email}}]
                },
                "saveToSentItems": "true"
            }
            response = requests.post(url, headers=headers, json=email_data)
            return response.status_code in [200, 202]
        except:
            return False
