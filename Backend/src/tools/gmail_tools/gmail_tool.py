from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .gmail_utility import authenticate_gmail, create_message, send_message
# from agentops.integrations.crewai import record_tool


import os

class GmailToolInput(BaseModel):
    """Input schema for GmailTool."""

    body: str = Field(..., description="The body of the email to send.")
    gmail: str = Field(..., description="The recipient's Gmail address.")


# @record_tool("This is used for gmail draft emails.")
class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = (
        "This tool is used to send a email with the provoded body to a client Gmail address."
    )
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, body: str, gmail: str) -> str:
        try:
            service = authenticate_gmail()

            sender = os.getenv("GMAIL_SENDER")
            to = gmail
            subject = "Blog post"
            message_text = body

            if not sender :
                return "Sender or recipient email not set in environment variables."

            message = create_message(sender, to, subject, message_text)
            sent = send_message(service, "me", message)

            if sent is None:
                return "Failed to send email."

            return f"Email sent successfully! Message ID: {sent['id']}"
        except Exception as e:
            return f"Error sending email: {e}"

