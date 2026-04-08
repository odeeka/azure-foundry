import hashlib
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool
from azure.identity import DefaultAzureCredential

load_dotenv()

AGENT_NAME = "WebSearchAgent-001"
STATE_FILE = Path(__file__).with_name(".websearch_agent_state.json")
INSTRUCTIONS = (
    "You are a research assistant that searches the web to find current, accurate answers to user questions."
)


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
        "tools": ["web_search_preview"],
    }
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def create_or_reuse_agent_version(
    foundry_client: AIProjectClient, agent_name: str, model_name: str, instructions: str
) -> dict:
    current_fingerprint = build_fingerprint(agent_name, model_name, instructions)
    state = load_state()

    if state.get("agent_name") == agent_name and state.get("fingerprint") == current_fingerprint:
        print(
            f"Agent definition unchanged. Reusing existing version"
            f" {state.get('version', 'unknown')} for {agent_name}."
        )
        return state

    # WebSearchPreviewTool is a built-in Foundry capability that lets the agent
    # query Bing to answer questions that need current external information.
    agent = foundry_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=instructions,
            tools=[WebSearchPreviewTool()],
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

    print(f"Agent version created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
    return state


def main() -> int:
    endpoint = require_env("FOUNDRY_PROJECT_ENDPOINT")
    model_name = require_env("MODEL_DEPLOYMENT_NAME")

    print(f"Connecting to Foundry project at {endpoint} using model {model_name}...")

    foundry_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    chat_client = foundry_client.get_openai_client()

    create_or_reuse_agent_version(
        foundry_client=foundry_client,
        agent_name=AGENT_NAME,
        model_name=model_name,
        instructions=INSTRUCTIONS,
    )

    # Start a fresh conversation for the request/response exchange.
    chat_session = chat_client.conversations.create()
    print(f"Created conversation with id: {chat_session.id}")

    # Ask a question that benefits from current web results.
    question = "What are the top 10 DevOps tools in 2026?"

    # Route the prompt to the named Foundry agent.
    response = chat_client.responses.create(
        conversation=chat_session.id,
        extra_body={
            "agent_reference": {
                "name": AGENT_NAME,
                "type": "agent_reference",
            }
        },
        input=question,
    )

    print(f"Agent response: {response.output_text}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Failed to run web search agent: {exc}", file=sys.stderr)
        raise SystemExit(1)

