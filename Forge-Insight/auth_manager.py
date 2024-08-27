import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from config import SCOPES, TOKEN_FILE, CLIENT_SECRET_FILE

class AuthManager:
    def __init__(self):
        self.creds = None

    def authenticate(self):
        if self.creds and self.creds.valid:
            return True
        
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            self.creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(self.creds.to_json())

        return True

    def get_credentials(self):
        if not self.creds:
            try:
                with open(TOKEN_FILE, 'r') as token:
                    self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except FileNotFoundError:
                return None
        return self.creds

    def clear_credentials(self):
        self.creds = None
        try:
            os.remove(TOKEN_FILE)
        except FileNotFoundError:
            pass