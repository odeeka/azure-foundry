# Python scripts

This folder contains small local smoke tests for the deployed Foundry environment.

## Files

- `chat_with_openai.py`: Uses `azure-ai-projects` with `DefaultAzureCredential`.
- `openapi_test.py`: Uses the OpenAI SDK against the Azure OpenAI-compatible endpoint.
- `.env`: Local developer settings only. Do not commit secrets.

## Setup

Create or update `.env` with safe local values:

```dotenv
AZURE_ENDPOINT=https://<your-foundry-account>.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=gpt-4-1-mini
AZURE_API_KEY=<optional-api-key>
```

Authenticate with Azure CLI if you use `chat_with_openai.py`:

```bash
az login
```

Install dependencies and run:

```bash
uv sync
uv run chat_with_openai.py
uv run openapi_test.py
```

These scripts are intended for development checks, not production use.
