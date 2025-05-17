"""
Provides tools for common operations with Gmail (e.g., send_mail)
"""

import os
from base64 import urlsafe_b64encode
from typing import Any, Optional, Dict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "gmail-mcp-server",
    version="0.1.0",
    description="Provides tools for common operations with Gmail (e.g., send_mail)"
)

class GoogleClient:
    """Encapsulates a Gmail API client."""
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self._creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        self.gmail = build("gmail", "v1", credentials=self._creds, cache_discovery=False)

def get_google_client(env_override: Optional[Dict[str, str]] = None) -> GoogleClient:
    """
    Constructs a GoogleClient using parameters from env_override (if provided), else from environment variables.
    """
    source = env_override if env_override is not None else os.environ
    client_id = source.get("CLIENT_ID")
    client_secret = source.get("CLIENT_SECRET")
    refresh_token = source.get("REFRESH_TOKEN")
    if not (client_id and client_secret and refresh_token):
        raise RuntimeError("Required Google OAuth credentials not found in environment or env_override parameter")
    return GoogleClient(client_id, client_secret, refresh_token)

@mcp.tool(name="send_mail", description="Send a new email to recipient(s) with a subject and body")
async def send_mail(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    env_override: Optional[Dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Sends an email using Gmail API.

    :param to: Recipient email address.
    :param subject: Email subject.
    :param body: Email body (can include HTML).
    :param cc: CC recipients, comma-separated.
    :param bcc: BCC recipients, comma-separated.
    :param env_override: (optional) Per-request env dict for Google OAuth credentials.
    :returns: Dict with 'content' list or error flag.
    """
    try:
        # Build MIME message headers
        headers = [
            'Content-Type: text/plain; charset="UTF-8"',
            'MIME-Version: 1.0',
            f"To: {to}",
            f"Cc: {cc}" if cc else None,
            f"Bcc: {bcc}" if bcc else None,
            f"Subject: {subject}",
        ]
        message = "\r\n".join(h for h in headers if h) + "\r\n\r\n" + body

        # base64url encode and strip padding
        raw = urlsafe_b64encode(message.encode("utf-8")).decode("ascii").rstrip("=")

        # get google client (from env_override or os.environ)
        google_client = get_google_client(env_override)

        # send via Gmail API
        sent = (
            google_client.gmail
            .users()
            .messages()
            .send(
                userId="me",
                body={"raw": raw},
            )
            .execute()
        )

        return {
            "content": [
                {"type": "text", "text": f"Email sent successfully. Message ID: {sent['id']}"}
            ]
        }
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error sending email: {e}"}
            ],
            "isError": True,
        }

if __name__ == "__main__":
    mcp.run(transport=os.getenv("TRANSPORT", "stdio"))