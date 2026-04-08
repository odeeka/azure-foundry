import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

load_dotenv()

STATE_FILE = Path(__file__).with_name(".agent_state.json")
AGENT_NAME = "infra-agent-001"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def build_fingerprint(agent_name: str, model_name: str, instructions: str) -> str:
    payload = {
        "agent_name": agent_name,
        "instructions": instructions,
        "model": model_name,
    }
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def create_or_reuse_agent_version(foundry_client: AIProjectClient, agent_name: str, model_name: str, instructions: str):
    current_fingerprint = build_fingerprint(agent_name, model_name, instructions)
    state = load_state()

    if state.get("agent_name") == agent_name and state.get("fingerprint") == current_fingerprint:
        print(
            "Agent definition unchanged. Reusing existing version"
            f" {state.get('version', 'unknown')} for {agent_name}."
        )
        return state

    agent = foundry_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=instructions,
        ),
    )

    state = {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "fingerprint": current_fingerprint,
        "model": model_name,
        "version": agent.version,
    }
    save_state(state)

    print(
        f"Agent version created (id: {agent.id}, name: {agent.name}, version: {agent.version})"
    )
    return state


def main() -> int:
    endpoint = require_env("FOUNDRY_PROJECT_ENDPOINT")
    model_name = require_env("MODEL_DEPLOYMENT_NAME")

    print("Connecting to Foundry project at:", endpoint)
    print("Using AI model deployment named:", model_name)

    foundry_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    infra_agent_instructions = """
You are "Terraform Infra Triage Buddy".

Help classify and triage Terraform and infrastructure issues.

Ask up to 2 clarifying questions if needed.

Always respond with:
1. Likely category
2. Quick checks (max 5 steps)
3. Ticket summary
4. Severity and why

Possible categories:
- Config issue
- Auth issue
- State issue
- Dependency issue
- Permissions issue
- Pipeline issue
- Network issue
- Unknown

Rules:
- Be concise.
- Do not guess missing technical details.
- Prefer safe checks first.
- If production, security, or shared infrastructure may be affected, mark severity High and recommend escalation.
""".strip()

    create_or_reuse_agent_version(
        foundry_client=foundry_client,
        agent_name=AGENT_NAME,
        model_name=model_name,
        instructions=infra_agent_instructions,
    )

    chat_client = foundry_client.get_openai_client()
    chat_session = chat_client.conversations.create()

    print(f"Created conversation with id: {chat_session.id}")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() in ["exit", "quit"]:
            print("Ending the conversation.")
            return 0

        if not user_message:
            continue

        infra_agent_reply = chat_client.responses.create(
            conversation=chat_session.id,
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "type": "agent_reference",
                }
            },
            input=user_message,
        )

        print(f"Infra Agent: {infra_agent_reply.output_text}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Failed to run infra triage agent: {exc}", file=sys.stderr)
        raise SystemExit(1)
