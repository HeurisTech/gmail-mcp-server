import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleClient:
    def __init__(self, *, client_id: str, client_secret: str, refresh_token: str):
        # No async needed here
        self._creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        self.gmail = build("gmail", "v1", credentials=self._creds)


def get_google_client():
    # Load Google OAuth credentials from environment
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    refresh_token = os.getenv("REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError(
            "Required Google OAuth credentials not found in environment variables"
        )
    
    return GoogleClient(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
    )