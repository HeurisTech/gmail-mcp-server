"""
Gmail MCP (Model Context Protocol) server
Provides tools for common operations with gmail.
"""

import json, os
from base64 import urlsafe_b64encode
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

mcp = FastMCP(
    "gmail-mcp",
    version="0.0.1",
    description="Gmail MCP (Model Context Protocol) server"
)

# Load Google OAuth credentials from environment
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")

if not client_id or not client_secret or not refresh_token:
    raise RuntimeError(
        "Required Google OAuth credentials not found in environment variables"
    )

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

google_client = GoogleClient(
    client_id=client_id,
    client_secret=client_secret,
    refresh_token=refresh_token,
)


@mcp.tool()
async def send_mail(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> dict[str, Any]:
    """
    Send a new email.

    :param to: Recipient email address.
    :param subject: Email subject.
    :param body: Email body (can include HTML).
    :param cc: CC recipients, comma-separated.
    :param bcc: BCC recipients, comma-separated.
    :returns: A dict with 'content' list or error flag.
    """
    try:
        # Build the raw MIME message
        headers = [
            'Content-Type: text/plain; charset="UTF-8"',
            'MIME-Version: 1.0',
            f"To: {to}",
            f"Cc: {cc}" if cc else None,
            f"Bcc: {bcc}" if bcc else None,
            f"Subject: {subject}",
        ]
        # drop any None entries
        headers = [h for h in headers if h]
        message = "\r\n".join(headers) + "\r\n\r\n" + body

        # base64url encode and strip padding
        raw = urlsafe_b64encode(message.encode("utf-8")).decode("ascii").rstrip("=")

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
    mcp.run()