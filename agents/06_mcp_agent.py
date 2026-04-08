# Import everything we need for setup
import os                                          # For reading environment variables
from dotenv import load_dotenv                      # For loading the .env file
from azure.identity import DefaultAzureCredential   # For automatic Azure authentication
from azure.ai.projects import AIProjectClient       # The main Azure AI Foundry client
from azure.ai.projects.models import (              # Classes for defining agents and tools
    PromptAgentDefinition,
    MCPTool,
)

# Read the .env file and load its values into environment variables
load_dotenv()

# my_endpoint: the URL of our Azure AI Foundry project
my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

# my_model: the name of the deployed AI model we want the agent to use
my_model = os.getenv("MODEL_DEPLOYMENT_NAME")

print(f"Endpoint: {my_endpoint}")
print(f"Model deployment: {my_model}")

# Create the Foundry client
# - endpoint: tells the SDK where our project lives
# - credential: proves we have permission to use it
foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential(),
)

# Get an OpenAI-compatible chat client from the Foundry client
# This is what we will use to send questions and receive answers
chat_client = foundry_client.get_openai_client()

# Create the MCP tool configuration
learn_tool = MCPTool(
    server_label="microsoft_learn_server",           # A human-readable label for this tool
    server_url="https://learn.microsoft.com/api/mcp", # The URL of the Microsoft Learn MCP server
    require_approval="never",                         # Let the agent use this tool without asking permission
)

# Create the agent with MCP tool attached
learn_agent = foundry_client.agents.create_version(
    agent_name="LearningResourceAgent-001",   # A unique name to identify this agent
    definition=PromptAgentDefinition(
        model=my_model,                      # The AI model that powers the agent's thinking
        instructions=(
            "You are an educational assistant that uses the Microsoft Learn MCP server "
            "to help users find relevant tutorials, documentation, and learning paths."
        ),
        tools=[learn_tool],                  # Give the agent access to our MCP tool
    )
)

# Confirm the agent was created successfully
print(f"MCP-enabled agent created! ID: {learn_agent.id}")

# Open a new conversation (chat session) with the agent
chat_session = chat_client.conversations.create()

# Print the session ID so we can reference it later
print(f"Chat session started! Session ID: {chat_session.id}")

# Write the question we want to ask the agent
learning_question = "Find me beginner-friendly learning paths for getting started with Azure cloud services."

# Send the question to the agent and get a response
# - conversation: links this message to our chat session
# - extra_body: tells the API to route this to our named agent
# - input: the actual question text
agent_response = chat_client.responses.create(
    conversation=chat_session.id,       # Use the chat session we created above
    extra_body={
        "agent_reference": {
            "name": "LearningResourceAgent-001",  # The name of the agent to use
            "type": "agent_reference"            # Tells the API this is an agent reference
        }
    },
    input=learning_question              # The question we want answered
)

# Print the agent's answer
print(f"Agent Response: {agent_response.output_text}")