import requests

class Mailgun:
    def __init__(self, domain, api_key):
        self.domain = domain
        self.api_key = api_key

    def send_email(self, from_email, to_email, subject, html_body):
        url = f"https://api.mailgun.net/v3/{self.domain}/messages"
        auth = ("api", self.api_key)
        data = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html_body
        }
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
