# os gives us access to environment variables
import os

# load_dotenv reads key-value pairs from a .env file into the environment
from dotenv import load_dotenv

# DefaultAzureCredential automatically figures out how you are logged in to Azure
from azure.identity import DefaultAzureCredential

# AIProjectClient is the main class for interacting with an Azure Foundry project
from azure.ai.projects import AIProjectClient

# PromptAgentDefinition lets us describe the agent's model, instructions, and tools
from azure.ai.projects.models import PromptAgentDefinition

# jsonref can load JSON files that use $ref pointers (common in OpenAPI specs)
import jsonref

# Load all variables from the .env file
load_dotenv()

# The URL of your Azure Foundry project
my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

# The name of the deployed model (e.g., GPT-4o) that the agent will use
my_model = os.getenv("MODEL_DEPLOYMENT_NAME")

# Build the Foundry client -- it needs the project endpoint and your Azure credentials
foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential(),
)

# Open the Bored Activity API spec file and parse it into a Python dictionary
# jsonref.loads resolves any $ref pointers so we get a fully expanded spec
with open("./activities_openapi.json", "r", encoding="utf-8") as spec_file:
    api_spec_data = jsonref.loads(spec_file.read())

# Build the tool configuration dictionary
# "type": "openapi" means this tool connects to an external REST API
# "name" is a label the agent uses internally to refer to this tool
# "spec" is the full OpenAPI specification we just loaded
# "auth" tells the SDK what credentials to send -- "anonymous" means none
api_tool_config = {
    "type": "openapi",
    "openapi": {
        "name": "activities",
        "spec": api_spec_data,
        "auth": {
            "type": "anonymous"
        },
    },
}

# Choose a unique name for this agent
api_agent_name = "ActivityAgent-001"

# Create the agent version with our model, instructions, and the activity tool
api_agent = foundry_client.agents.create_version(
    agent_name=api_agent_name,
    definition=PromptAgentDefinition(
        # Which language model powers this agent
        model=my_model,
        # System-level instructions that guide the agent's personality and behavior
        instructions="You are a helpful activity planner. When someone is looking for something to do, use the activity API to find suggestions by category (e.g. education, recreational, social, cooking, relaxation, diy, music). Present the results in a friendly, organized way.",
        # Attach the activity API tool so the agent can make real API calls
        tools=[api_tool_config],
    ),
)

# Confirm creation and print useful details
print(f"Agent ready -- ID: {api_agent.id}, Name: {api_agent.name}, Version: {api_agent.version}")

# Get an OpenAI-compatible client from the Foundry project
chat_client = foundry_client.get_openai_client()

# Open a new conversation thread for this session
chat_session = chat_client.conversations.create()

# Print the conversation ID so we can reference it later if needed
print(f"Conversation started -- ID: {chat_session.id}")

# The question we want answered -- the agent will use the activity API to look this up
user_question = "I'm bored and want to learn something new. Can you suggest some educational activities?"

# Send the question to the activity agent through our conversation
result = chat_client.responses.create(
    # Link this message to the conversation we opened above
    conversation=chat_session.id,
    # Tell the service which agent should handle this request
    extra_body={
        "agent_reference": {
            "name": api_agent_name,
            "type": "agent_reference",
        }
    },
    # The actual question
    input=user_question,
)

# Display the agent's answer
print(f"Activity Agent: {result.output_text}")