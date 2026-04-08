import os
import sys

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool
from azure.identity import DefaultAzureCredential

load_dotenv()

AGENT_NAME = "WebSearchAgent-001"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def main() -> int:
    endpoint = require_env("FOUNDRY_PROJECT_ENDPOINT")
    model_name = require_env("MODEL_DEPLOYMENT_NAME")

    print(f"Connecting to Foundry project at {endpoint} using model {model_name}...")

    foundry_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    chat_client = foundry_client.get_openai_client()

    # Create a web-enabled prompt agent backed by the configured model.
    # WebSearchPreviewTool is a built-in Foundry capability that lets the agent
    # query Bing to answer questions that need current external information.
    foundry_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions="You are a research assistant that searches the web to find current, accurate answers to user questions.",
            tools=[WebSearchPreviewTool()],
        ),
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

