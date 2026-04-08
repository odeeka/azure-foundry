# Agents Folder

This folder contains small Azure AI Foundry agent prototypes for infrastructure triage and web-backed research.

## Purpose

The scripts in this folder are local experiments that show two Foundry agent patterns:

- an infra triage agent for Terraform and platform issue classification
- a web-search agent that uses a built-in search tool for current-answer retrieval

Both are suitable for local demos and prompt iteration, not for production use.

## Files

- `01_infra_triage.py`: Main script. Connects to Azure AI Foundry, creates a prompt agent version only when the definition changes, starts a conversation, and runs a local chat loop.
- `02_websearch_agent.py`: Sample script. Connects to Azure AI Foundry, creates a web-search-enabled prompt agent, opens a conversation, submits one question, and prints the response.
- `03_code_interpreter_agent.py`: Analysis script. Connects to Azure AI Foundry, creates a code interpreter agent version that includes an uploaded dataset file, submits a sales analysis prompt, retries on rate-limit errors with exponential backoff, and downloads the generated chart to the local folder.
- `04_openapi_agent.py`: Demo script. Connects to Azure AI Foundry, creates a prompt agent with an OpenAPI tool attached to the Bored Activity API, opens a conversation, submits one question, and prints the response. The file uses inline comments throughout to explain each step.
- `activities_openapi.json`: OpenAPI spec for the Bored Activity API, used by `04_openapi_agent.py`.
- `bookstore_sales.csv`: Sample dataset used by `03_code_interpreter_agent.py`.
- `.env.example`: Example environment variables required by the scripts.
- `.env`: Local developer configuration. This should stay untracked.
- `pyproject.toml`: Python project metadata and dependencies.
- `uv.lock`: Locked dependency versions for reproducible local installs.

## What The Code Does

### 01 Infra Triage Agent

The flow in `01_infra_triage.py` is:

1. Load environment variables from `.env` using `python-dotenv`.
2. Read two required inputs:
	- `FOUNDRY_PROJECT_ENDPOINT`
	- `MODEL_DEPLOYMENT_NAME`
3. Authenticate with Azure using `DefaultAzureCredential`.
4. Create an `AIProjectClient` connected to the Foundry project.
5. Build a fingerprint from the agent definition.
6. Create a new version of the prompt agent only if that fingerprint changed since the last run.
7. Create an OpenAI-compatible conversation session.
8. Enter a terminal chat loop and send each user message to the Foundry agent using `agent_reference`.

### 02 Web Search Agent

The flow in `02_websearch_agent.py` is:

1. Load environment variables from `.env`.
2. Read the Foundry project endpoint and model deployment name.
3. Authenticate with Azure using `DefaultAzureCredential`.
4. Create an `AIProjectClient` and OpenAI-compatible chat client.
5. Create a prompt agent named `WebSearchAgent-001`.
6. Attach the built-in `WebSearchPreviewTool` so the agent can use live web search.
7. Create a new conversation.
8. Submit a single research question and print the returned answer.

### 03 Code Interpreter Agent

The flow in `03_code_interpreter_agent.py` is:

1. Load environment variables from `.env`.
2. Read `FOUNDRY_PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME`.
3. Authenticate with Azure using `DefaultAzureCredential`.
4. Create an `AIProjectClient` and OpenAI-compatible chat client.
5. Compute a SHA-256 hash of `bookstore_sales.csv` and build a compound fingerprint from model name, instructions, and the dataset hash.
6. If the fingerprint matches the previous run, reuse the existing agent version and uploaded file ID.
7. Otherwise, upload the CSV to the Foundry files store and create a new agent version with a `CodeInterpreterTool` that references the uploaded file.
8. Start a conversation and submit the analysis prompt.
9. Retry the API call with exponential backoff if the deployment returns a `RateLimitError`.
10. Walk the response output annotations in reverse to find a `container_file_citation` that references the generated chart.
11. Download the chart file to the local folder.

### 04 OpenAPI Tool Agent

The flow in `04_openapi_agent.py` is:

1. Load environment variables from `.env`.
2. Read the Foundry project endpoint and model deployment name.
3. Authenticate with Azure using `DefaultAzureCredential`.
4. Load `activities_openapi.json` with `jsonref.loads` to resolve any `$ref` pointers into a fully expanded spec.
5. Create an `AIProjectClient` and OpenAI-compatible chat client.
6. Build a tool configuration dict of type `"openapi"` containing the resolved spec and anonymous auth.
7. Create an agent version with the OpenAPI tool attached so the agent can make real REST calls to the activity API.
8. Open a new conversation and submit a question that benefits from live activity suggestions.
9. Print the agent's response.

## Agent Behavior

### Infra Triage Agent

The agent is configured with infrastructure triage instructions. It is designed to:

- classify likely issue type
- suggest a short list of safe checks
- produce a ticket-style summary
- assign a severity with explanation

The prompt specifically targets these categories:

- Config issue
- Auth issue
- State issue
- Dependency issue
- Permissions issue
- Pipeline issue
- Network issue
- Unknown

### Web Search Agent

The web search agent is configured as a research assistant. It is designed to:

- answer questions that need current external information
- use the built-in web search tool when the prompt requires live data
- return a single text response for the requested query

Its current sample prompt is:

- `What are the top 10 DevOps tools in 2026?`

## Dependencies

Defined in `pyproject.toml`:

- `azure-ai-projects`
- `azure-identity`
- `openai`
- `python-dotenv`

The script depends mainly on these Azure SDK types:

- `AIProjectClient`
- `PromptAgentDefinition`
- `WebSearchPreviewTool`
- `DefaultAzureCredential`

## Prerequisites

- Python 3.12+
- `uv` for dependency management
- An Azure AI Foundry project
- A deployed model in that project
- Working Azure authentication, usually via `az login`

## Configuration

Copy `.env.example` to `.env` and set the values:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://<your-foundry-project-endpoint>
MODEL_DEPLOYMENT_NAME=gpt-4-1-mini
```

Notes:

- `FOUNDRY_PROJECT_ENDPOINT` should be the Foundry project endpoint expected by `AIProjectClient`, not just a generic cognitive services endpoint.
- `MODEL_DEPLOYMENT_NAME` must match a deployment that already exists in the target Foundry project.

## Running The Script

Install dependencies:

```bash
uv sync
```

Authenticate to Azure:

```bash
az login
```

Run the agent script:

```bash
uv run 01_infra_triage.py
```

Type messages in the terminal. Use `exit` or `quit` to stop.

Run the web-search example:

```bash
uv run 02_websearch_agent.py
```

This script runs once, sends a predefined question, and exits after printing the response.

## Important Implementation Notes

- The script stores a local fingerprint in `.agent_state.json`.
- A new agent version is created only when the local agent definition changes.
- If the fingerprint is unchanged, the script reuses the previously published version.
- The script opens a fresh conversation on each run.
- There is no remote reconciliation step if the local state file is deleted.
- There is no exception handling around authentication, agent creation, or chat requests.
- The script is stateful only for the current terminal session.
- `02_websearch_agent.py` currently creates a new agent version every time it runs.
- `02_websearch_agent.py` uses a hard-coded example prompt rather than terminal input.
- `02_websearch_agent.py` does not yet persist or reuse agent version state.

## Production Readiness

This folder is currently experimental.

It is useful for:

- prompt iteration
- local demos
- manual triage testing

It is not production-ready because it does not include:

- structured error handling
- retry logic
- agent lifecycle management
- logging/telemetry
- tests
- configuration validation
- non-interactive execution paths

## Practical Improvements

1. Add input validation for required environment variables before client creation.
2. Add exception handling around Foundry and chat API calls.
3. Add remote reconciliation so the script can recover if `.agent_state.json` is missing.
4. Add transcript logging for debugging and auditability.
5. Apply the same version-reuse pattern from `01_infra_triage.py` to `02_websearch_agent.py`.
6. Split agent creation and chat execution into separate functions or modules for easier testing.
