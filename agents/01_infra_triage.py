import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
my_model = os.getenv("MODEL_DEPLOYMENT_NAME")

print("Connecting to Foundry project at:", my_endpoint)
print("Using AI model deployment named:", my_model)

# Create the Foundry client
foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential(),
)

# Agent name
infra_agent_name = "infra-agent-001"

# Agent instructions
infra_agent_instructions = """
You are "Terraform Infra Triage Buddy".

Help classify and triage Terraform and infrastructure issues.

Ask up to 2 clarifying questions if needed.

Always respond with:
1. Likely category
2. Quick checks (max 5 steps)
3. Ticket summary
4. Severity and why

Possible categories:
- Config issue
- Auth issue
- State issue
- Dependency issue
- Permissions issue
- Pipeline issue
- Network issue
- Unknown

Rules:
- Be concise.
- Do not guess missing technical details.
- Prefer safe checks first.
- If production, security, or shared infrastructure may be affected, mark severity High and recommend escalation.
""".strip()

# Create a new agent version
infra_agent = foundry_client.agents.create_version(
    agent_name=infra_agent_name,
    definition=PromptAgentDefinition(
        model=my_model,
        instructions=infra_agent_instructions,
    ),
)

print(
    f"Agent created (id: {infra_agent.id}, name: {infra_agent.name}, version: {infra_agent.version})"
)

# Get an OpenAI-compatible chat client from our Foundry connection
# This client knows how to send messages and receive replies
chat_client = foundry_client.get_openai_client()

# Start a brand-new conversation (like opening a fresh chat window)
# The conversation stores the full history so the agent has context
chat_session = chat_client.conversations.create()

# Show the conversation ID so we know it was created
print(f"Created conversation with id: {chat_session.id}")

# This flag keeps the chat loop running — set it to False to stop
is_chatting = True

while is_chatting:
    # Wait for the user to type a message
    user_message = input("You: ")

    # If the user types "exit" or "quit", end the conversation
    if user_message.lower() in ["exit", "quit"]:
        is_chatting = False
        print("Ending the conversation. Stay active and healthy!")
    else:
        # Send the user's message to the Fitness Coach agent and get a reply
        # - conversation: links this message to our ongoing chat session
        # - extra_body: tells Foundry which agent should respond
        # - input: the actual message text from the user
        infra_agent_reply = chat_client.responses.create(
            conversation=chat_session.id,
            extra_body={
                "agent_reference": {
                    "name": infra_agent_name,
                    "type": "agent_reference"
                }
            },
            input=user_message
        )

        # Display the agent's response
        print(f"Infra Agent: {infra_agent_reply.output_text}")
