import hashlib
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import RateLimitError
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool, AutoCodeInterpreterToolParam
from azure.identity import DefaultAzureCredential

load_dotenv()

DATA_FILE = Path(__file__).with_name("bookstore_sales.csv")
AGENT_NAME = "BookstoreAnalyst-001"
STATE_FILE = Path(__file__).with_name(".code_interpreter_agent_state.json")
ANALYSIS_PROMPT = (
    "Calculate total revenue (unit_price * quantity) for each genre and create a horizontal bar chart "
    "showing revenue by genre, sorted from highest to lowest. Then summarize the top-performing genre "
    "and the highest-volume title."
)
AGENT_INSTRUCTIONS = (
    "You are a data analyst for an independent bookstore. You write and execute Python code to explore "
    "sales data, calculate revenue, identify best-selling categories and titles, and create clear labeled "
    "visualizations. Always explain your findings briefly and accurately."
)
MAX_RETRIES = 4
INITIAL_RETRY_DELAY_SECONDS = 2


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def compute_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_agent_fingerprint(model_name: str, instructions: str, dataset_hash: str) -> str:
    payload = {
        "agent_name": AGENT_NAME,
        "dataset_hash": dataset_hash,
        "instructions": instructions,
        "model": model_name,
    }
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def upload_dataset(chat_client, data_file: Path):
    with data_file.open("rb") as file_handle:
        uploaded_file = chat_client.files.create(
            purpose="assistants",
            file=file_handle,
        )

    print(f"File uploaded successfully -- ID: {uploaded_file.id}")
    return uploaded_file


def create_or_reuse_agent_version(foundry_client: AIProjectClient, chat_client, model_name: str, data_file: Path) -> dict:
    dataset_hash = compute_file_hash(data_file)
    fingerprint = build_agent_fingerprint(model_name, AGENT_INSTRUCTIONS, dataset_hash)
    state = load_state()

    if (
        state.get("fingerprint") == fingerprint
        and state.get("uploaded_file_id")
        and state.get("agent_name") == AGENT_NAME
    ):
        print(
            "Agent definition unchanged. Reusing existing version"
            f" {state.get('version', 'unknown')} and file {state['uploaded_file_id']}."
        )
        return state

    uploaded_file = upload_dataset(chat_client, data_file)
    agent = foundry_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=AGENT_INSTRUCTIONS,
            tools=[
                CodeInterpreterTool(
                    container=AutoCodeInterpreterToolParam(
                        file_ids=[uploaded_file.id]
                    )
                )
            ],
        ),
    )

    state = {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "dataset_hash": dataset_hash,
        "fingerprint": fingerprint,
        "model": model_name,
        "uploaded_file_id": uploaded_file.id,
        "version": agent.version,
    }
    save_state(state)

    print(
        f"Agent ready -- ID: {agent.id}, Name: {agent.name}, Version: {agent.version}"
    )
    return state


def extract_generated_file_reference(analysis_result):
    for output_item in reversed(analysis_result.output):
        if output_item.type != "message":
            continue

        for content_item in reversed(output_item.content):
            if content_item.type != "output_text" or not content_item.annotations:
                continue

            for annotation in reversed(content_item.annotations):
                if annotation.type == "container_file_citation":
                    return annotation.file_id, annotation.filename, annotation.container_id

    return "", "", ""


def download_generated_file(chat_client, file_id: str, filename: str, container_id: str) -> None:
    raw_content = chat_client.containers.files.content.retrieve(
        file_id=file_id,
        container_id=container_id,
    )

    output_path = Path(__file__).with_name(filename)
    with output_path.open("wb") as local_file:
        local_file.write(raw_content.read())

    print(f"Downloaded: {output_path.name}")
    print(f"Chart saved and ready to view: {output_path}")


def create_response_with_retry(chat_client, conversation_id: str, agent_name: str):
    delay_seconds = INITIAL_RETRY_DELAY_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return chat_client.responses.create(
                conversation=conversation_id,
                input=ANALYSIS_PROMPT,
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
            )
        except RateLimitError as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    "The Foundry model deployment is rate limited. Wait a minute and retry, or increase the deployment quota/capacity."
                ) from exc

            print(
                f"Rate limited on attempt {attempt}/{MAX_RETRIES}. "
                f"Retrying in {delay_seconds} seconds..."
            )
            time.sleep(delay_seconds)
            delay_seconds *= 2


def main() -> int:
    endpoint = require_env("FOUNDRY_PROJECT_ENDPOINT")
    model_name = require_env("MODEL_DEPLOYMENT_NAME")

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    print(f"Connecting to Foundry project at {endpoint} using model {model_name}...")

    foundry_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    chat_client = foundry_client.get_openai_client()
    agent_state = create_or_reuse_agent_version(foundry_client, chat_client, model_name, DATA_FILE)

    chat_session = chat_client.conversations.create()
    print(f"Conversation started -- ID: {chat_session.id}")

    analysis_result = create_response_with_retry(
        chat_client=chat_client,
        conversation_id=chat_session.id,
        agent_name=agent_state["agent_name"],
    )

    print(f"Analysis complete -- Response ID: {analysis_result.id}")
    print(f"Agent response: {analysis_result.output_text}")

    output_file_id, output_filename, output_container_id = extract_generated_file_reference(analysis_result)

    if output_file_id and output_filename:
        download_generated_file(chat_client, output_file_id, output_filename, output_container_id)
        return 0

    print("The agent did not generate a downloadable file this time.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Failed to run code interpreter agent: {exc}", file=sys.stderr)
        raise SystemExit(1)
