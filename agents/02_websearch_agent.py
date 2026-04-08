import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool
from azure.identity import DefaultAzureCredential

load_dotenv()

my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
my_model = os.getenv("MODEL_DEPLOYMENT_NAME")

print(f"Connecting to Foundry project at {my_endpoint} using model {my_model}...")

foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential(),
)

chat_client = foundry_client.get_openai_client()

# Create a web-enabled prompt agent backed by the configured model.
web_search_agent = foundry_client.agents.create_version(
    agent_name="WebSearchAgent-001",
    definition=PromptAgentDefinition(
        model=my_model,
        instructions="You are a research assistant that searches the web to find current, accurate answers to user questions.",
        tools=[
            WebSearchPreviewTool()
        ]
    )
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
            "name": "WebSearchAgent-001",
            "type": "agent_reference"
        }
    },
    input=question
)

print(f"Agent response: {response.output_text}")
