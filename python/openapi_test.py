import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} not set")
    return value


def normalize_openai_base_url(endpoint_base: str) -> str:
    if endpoint_base.endswith("/"):
        endpoint_base = endpoint_base[:-1]

    if endpoint_base.endswith(".openai.azure.com"):
        return f"{endpoint_base}/openai/v1/"

    return endpoint_base.replace(
        ".cognitiveservices.azure.com",
        ".openai.azure.com/openai/v1/",
    )


def main() -> int:
    endpoint_base = require_env("AZURE_ENDPOINT")
    api_key = require_env("AZURE_API_KEY")
    model_name = os.environ.get("MODEL_DEPLOYMENT_NAME", "example-cd")

    client = OpenAI(
        base_url=normalize_openai_base_url(endpoint_base),
        api_key=api_key,
        timeout=30.0,
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "What is the capital of Hungary?"},
                {"role": "user", "content": "What is the capital of Germany?"},
            ],
        )
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    print(completion.choices[0].message.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
