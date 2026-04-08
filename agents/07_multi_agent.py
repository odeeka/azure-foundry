# os lets us read environment variables
import os

# load_dotenv reads your .env file and sets the variables for this session
from dotenv import load_dotenv

# DefaultAzureCredential handles authentication automatically
from azure.identity import DefaultAzureCredential

# AIProjectClient is the main gateway to Azure Foundry
from azure.ai.projects import AIProjectClient

# PromptAgentDefinition defines how our agent behaves
# MCPTool lets us connect to a Model Context Protocol server
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# jsonref resolves $ref pointers inside JSON files (needed for OpenAPI specs)
import jsonref

# Pull in all environment variables from the .env file
load_dotenv()

# The Foundry project URL that the SDK will call
my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

# Which deployed language model the agent should use
my_model = os.getenv("MODEL_DEPLOYMENT_NAME")

print(f"Project endpoint: {my_endpoint}")
print(f"Language model: {my_model}")

# Initialize the Foundry client with our endpoint and credentials
foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential(),
)
print("Foundry client initialized successfully.")

# This returns an OpenAI-compatible client already wired to your Foundry project
chat_client = foundry_client.get_openai_client()

# Open the OpenAPI spec file and parse it, resolving any internal $ref pointers
with open("./activities_openapi.json", "r", encoding="utf-8") as spec_file:
    activity_api_spec = jsonref.loads(spec_file.read())

# Package the parsed spec into a tool dictionary the agent understands
# "type": "openapi" tells the agent this is an external API it can call
# "auth": {"type": "anonymous"} means no API key is required
activity_api_tool = {
    "type": "openapi",
    "openapi": {
        "name": "activities",
        "spec": activity_api_spec,
        "auth": {
            "type": "anonymous"
        },
    },
}

# Create an MCP tool that points to the Microsoft Learn search endpoint
# server_label is a friendly name you pick for this tool
# server_url is the public MCP endpoint provided by Microsoft
# require_approval="never" means the agent can call it without asking permission first
learn_mcp_tool = MCPTool(
    server_label="microsoft_learn_server",
    server_url="https://learn.microsoft.com/api/mcp",
    require_approval="never",
)

# Pick a descriptive name for this multi-tool agent
multi_agent_name = "MultiAssistantAgent-001"

# Register the agent in Foundry with both tools attached
multi_agent = foundry_client.agents.create_version(
    agent_name=multi_agent_name,
    definition=PromptAgentDefinition(
        # The language model that powers this agent
        model=my_model,
        # High-level instructions telling the agent what it can do
        instructions="You are a helpful assistant with two skills: (1) you can suggest fun activities using the Bored Activity API, and (2) you can search Microsoft Learn documentation. Use whichever tool is appropriate for the user's question, or both if the question covers multiple topics.",
        # Pass both tools as a list -- the agent can use either or both in a single response
        tools=[activity_api_tool, learn_mcp_tool],
    ),
)

# Confirm the agent was created
print(f"Agent created -- Name: {multi_agent.name}, ID: {multi_agent.id}")

# Start a brand-new conversation thread
chat_session = chat_client.conversations.create()

# Print the session ID for debugging
print(f"Chat session opened -- ID: {chat_session.id}")

# This question intentionally covers two different topics so the agent must use both tools
test_question = "I'm bored, suggest a few activities I can try, and also find me a Microsoft Learn tutorial about deploying Azure Functions."

# Send the question to our multi-tool agent
result = chat_client.responses.create(
    # Attach this message to the conversation we opened earlier
    conversation=chat_session.id,
    # Tell the service which agent should handle this request
    extra_body={
        "agent_reference": {
            "name": multi_agent_name,
            "type": "agent_reference",
        }
    },
    # The user's question
    input=test_question,
)

# Show the agent's combined answer
print(f"Agent response: {result.output_text}")
