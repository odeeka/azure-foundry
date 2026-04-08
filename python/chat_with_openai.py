import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


def main() -> int:
    endpoint = require_env("AZURE_ENDPOINT")
    model_name = require_env("MODEL_DEPLOYMENT_NAME")

    try:
        foundry_client = AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )
        chat_client = foundry_client.get_openai_client()

        prompts = [
            (
                "Respond only in JSON with fields: use_case, benefits, risks.",
                "Describe using AI in customer support.",
            ),
            (
                "Answer like a senior cloud architect.",
                "Why should a company adopt AI in their infrastructure?",
            ),
        ]

        for instructions, prompt in prompts:
            response = chat_client.responses.create(
                model=model_name,
                instructions=instructions,
                input=prompt,
            )
            print(response.output_text)
            print("---")
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
