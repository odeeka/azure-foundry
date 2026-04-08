#!/usr/bin/env bash

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required" >&2
    exit 1
fi

: "${AZURE_ENDPOINT:?AZURE_ENDPOINT must be set}"
: "${AZURE_API_KEY:?AZURE_API_KEY must be set}"

MODEL_DEPLOYMENT_NAME="${MODEL_DEPLOYMENT_NAME:-gpt-4-1-mini}"
OPENAI_ENDPOINT="${AZURE_ENDPOINT%/}"
OPENAI_ENDPOINT="${OPENAI_ENDPOINT/.cognitiveservices.azure.com/.openai.azure.com}"

response="$({
    curl --silent --show-error --fail-with-body \
        -X POST "${OPENAI_ENDPOINT}/openai/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${AZURE_API_KEY}" \
        -d "{
            \"messages\": [
                {\"role\": \"user\", \"content\": \"What is the capital of Hungary?\"},
                {\"role\": \"user\", \"content\": \"What is the capital of Germany?\"}
            ],
            \"model\": \"${MODEL_DEPLOYMENT_NAME}\"
        }"
} )"

echo "${response}" | jq -r '.choices[0].message.content'