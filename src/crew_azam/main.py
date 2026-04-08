#!/usr/bin/env python
import os
import sys
import warnings

from datetime import datetime

from crew_azam.crew import CrewAzam
from crew_azam.gmail_polling import GmailPollingService


def _safe_key_fingerprint(key: str) -> str:
    if not key:
        return "<empty>"
    if len(key) < 10:
        return "<too-short>"
    return f"{key[:8]}...{key[-4:]}"


def _prefer_dotenv_for_scan() -> None:
    """Override selected runtime env vars with values from .env for scan flow."""
    from dotenv import dotenv_values

    dotenv_path = os.getenv("SCAN_DOTENV_PATH", ".env")
    dotenv_values_map = dotenv_values(dotenv_path)

    override_keys = (
        "ANTHROPIC_API_KEY",
        "MODEL",
        "GMAIL_CREDENTIALS_PATH",
        "GMAIL_TOKEN_PATH",
        "GMAIL_QUERY",
        "GMAIL_MAX_RESULTS",
        "GMAIL_MARK_AS_READ",
    )

    for key in override_keys:
        value = dotenv_values_map.get(key)
        if value is not None and value != "":
            os.environ[key] = str(value)

    key = os.getenv("ANTHROPIC_API_KEY", "")
    model = os.getenv("MODEL", "<unset>")
    print(
        "scan env source: .env preferred | "
        f"MODEL={model} | ANTHROPIC_API_KEY={_safe_key_fingerprint(key)}"
    )

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        CrewAzam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        CrewAzam().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CrewAzam().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        CrewAzam().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = CrewAzam().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")


def scan_unread_emails():
    """Manually scan unread Gmail messages and process each one with receive_email_task."""
    _prefer_dotenv_for_scan()

    credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "secrets/client_secret_archy.json")
    token_path = os.getenv("GMAIL_TOKEN_PATH", "secrets/gmail_token.json")
    query = os.getenv("GMAIL_QUERY", "in:inbox is:unread")
    max_results = int(os.getenv("GMAIL_MAX_RESULTS", "10"))
    mark_as_read = os.getenv("GMAIL_MARK_AS_READ", "true").lower() == "true"

    poller = GmailPollingService(credentials_path=credentials_path, token_path=token_path)
    messages = poller.list_unread(query=query, max_results=max_results)

    if not messages:
        print("No unread messages matched the Gmail query.")
        return

    print(f"Found {len(messages)} unread message(s).")
    email_crew = CrewAzam().email_crew()

    for message in messages:
        print(f"Processing message: {message.message_id} | {message.subject}")
        inputs = {
            "topic": "",
            "current_year": str(datetime.now().year),
            "email_message_id": message.message_id,
            "email_thread_id": message.thread_id,
            "email_from": message.sender,
            "email_sender_address": message.sender_email,
            "email_subject": message.subject,
            "email_body": message.body,
            "email_attachments": ", ".join(message.attachments) if message.attachments else "None",
        }

        try:
            email_crew.kickoff(inputs=inputs)
            if mark_as_read:
                poller.mark_as_read(message.message_id)
        except Exception as exc:
            print(f"Failed to process message {message.message_id}: {exc}")
