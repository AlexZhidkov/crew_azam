from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from email.utils import parseaddr
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


@dataclass
class GmailMessage:
	message_id: str
	thread_id: str
	sender: str
	sender_email: str
	subject: str
	body: str
	attachments: list[str]


class GmailPollingService:
	def __init__(self, credentials_path: str, token_path: str) -> None:
		self.credentials_path = credentials_path
		self.token_path = token_path
		self.service = self._build_service()

	def _build_service(self):
		creds = None
		if os.path.exists(self.token_path):
			creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
				creds = flow.run_local_server(port=0)

			token_dir = Path(self.token_path).parent
			token_dir.mkdir(parents=True, exist_ok=True)
			with open(self.token_path, "w", encoding="utf-8") as token_file:
				token_file.write(creds.to_json())

		return build("gmail", "v1", credentials=creds)

	def list_unread(self, query: str, max_results: int) -> list[GmailMessage]:
		try:
			response = self.service.users().messages().list(
				userId="me",
				q=query,
				maxResults=max_results,
			).execute()
		except HttpError as exc:
			raise RuntimeError(f"Gmail list_unread failed: {exc}") from exc

		messages = response.get("messages", [])
		results: list[GmailMessage] = []
		for item in messages:
			full_message = self.service.users().messages().get(
				userId="me",
				id=item["id"],
				format="full",
			).execute()
			results.append(self._to_gmail_message(full_message))

		return results

	def mark_as_read(self, message_id: str) -> None:
		self.service.users().messages().modify(
			userId="me",
			id=message_id,
			body={"removeLabelIds": ["UNREAD"]},
		).execute()

	def _to_gmail_message(self, message: dict[str, Any]) -> GmailMessage:
		payload = message.get("payload", {})
		headers = payload.get("headers", [])

		subject = self._header_value(headers, "Subject")
		sender = self._header_value(headers, "From")
		sender_email = parseaddr(sender)[1]
		body = self._extract_plain_text(payload).strip()

		return GmailMessage(
			message_id=message.get("id", ""),
			thread_id=message.get("threadId", ""),
			sender=sender,
			sender_email=sender_email,
			subject=subject,
			body=body,
			attachments=[],
		)

	@staticmethod
	def _header_value(headers: list[dict[str, str]], key: str) -> str:
		for header in headers:
			if header.get("name", "").lower() == key.lower():
				return header.get("value", "")
		return ""

	def _extract_plain_text(self, payload: dict[str, Any]) -> str:
		mime_type = payload.get("mimeType", "")
		body_data = payload.get("body", {}).get("data")

		if mime_type == "text/plain" and body_data:
			return self._decode_base64(body_data)

		parts = payload.get("parts", [])
		for part in parts:
			content = self._extract_plain_text(part)
			if content:
				return content

		if body_data:
			return self._decode_base64(body_data)

		return ""

	@staticmethod
	def _decode_base64(value: str) -> str:
		padded = value + "=" * (-len(value) % 4)
		decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
		return decoded.decode("utf-8", errors="replace")
