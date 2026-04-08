# CrewAzam Crew

Welcome to the CrewAzam Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:

```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/crew_azam/config/agents.yaml` to define your agents
- Modify `src/crew_azam/config/tasks.yaml` to define your tasks
- Modify `src/crew_azam/crew.py` to add your own logic, tools and specific args
- Modify `src/crew_azam/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the crew-azam Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Manual Gmail Unread Scan

You can manually trigger Gmail unread-email processing and run only `receive_email_task`.

### 1) Create Google API credentials

- In Google Cloud, enable Gmail API.
- Create OAuth Desktop credentials.
- Save the JSON file as `secrets/gmail_credentials.json`.

### 2) Configure environment variables

Add these values in your `.env` file (or export them in your shell):

```bash
GMAIL_CREDENTIALS_PATH=secrets/gmail_credentials.json
GMAIL_TOKEN_PATH=secrets/gmail_token.json
GMAIL_QUERY=in:inbox is:unread
GMAIL_MAX_RESULTS=10
GMAIL_MARK_AS_READ=true
GMAIL_ATTACHMENTS_DIR=data/attachments
```

Notes:

- First run opens a browser for OAuth consent and creates `GMAIL_TOKEN_PATH`.
- `GMAIL_MARK_AS_READ=true` prevents reprocessing the same email.
- The manual scan command prefers values from `.env` (including `ANTHROPIC_API_KEY` and `MODEL`) even if different values are already exported in your shell.

Optional:

- Use `SCAN_DOTENV_PATH=/path/to/.env` to point to a different env file for scan runs.

### 3) Run the manual scan

```bash
uv run scan_unread_emails
```

This command:

- Fetches unread emails from Gmail using `GMAIL_QUERY`.
- Downloads message attachments into `GMAIL_ATTACHMENTS_DIR`.
- Triggers `receive_email_task` once per unread message.
- Marks processed messages as read when enabled.

## Understanding Your Crew

The crew-azam Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the CrewAzam Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
