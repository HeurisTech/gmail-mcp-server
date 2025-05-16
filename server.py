"""
Provides tools for common operations with gmail (e.g., send_mail)
"""

from base64 import urlsafe_b64encode
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from google_client import get_google_client

mcp = FastMCP(
    "gmail-mcp-server",
    version="0.1.0",
    description="Provides tools for common operations with gmail (e.g., send_mail)"
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

        # get google client
        google_client = get_google_client()

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