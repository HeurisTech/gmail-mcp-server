#!/usr/bin/env python3
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
]

def get_refresh_token():
    # Perform OAuth flow via local server
    flow = InstalledAppFlow.from_client_secrets_file(
        Path.cwd() / "credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=4321)

    # Extract the pieces we care about
    data = {
        "refresh_token":  creds.refresh_token,
        "client_id":      creds.client_id,
        "client_secret":  creds.client_secret,
        "token_uri":      creds.token_uri,
        "scopes":         creds.scopes,
    }

    # Print to console
    print("\nRefresh Token:", data["refresh_token"])
    print("Client ID:     ", data["client_id"])
    print("Client Secret: ", data["client_secret"])

    # Save to token.json
    with open("token.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nCredentials saved to token.json")

if __name__ == "__main__":
    get_refresh_token()