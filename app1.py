import os  # For accessing environment variables
from azure.ai.projects import AIProjectClient  # Azure AI Foundry project client
from azure.identity import DefaultAzureCredential  # For Azure authentication
from azure.ai.projects.models import BingGroundingTool  # Bing search tool for agent
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Create an Azure AI Project client using credentials and connection string from environment
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),  # Use default Azure credentials
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]  # Connection string from environment
)

# Retrieve Bing connection using the connection name from environment
bing_connection = project_client.connections.get(
    connection_name=os.environ["BING_CONNECTION"]
)
conn_id = bing_connection.id  # Get the connection ID

print(conn_id)  # Print the Bing connection ID

# Initialize Bing grounding tool with the connection ID
bing = BingGroundingTool(connection_id=conn_id)

# Create agent with Bing tool and process assistant run
with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4",  # Use GPT-4 model
        name="ai-agent-demo",  # Name of the agent
        instructions="You are a helpful assistant",  # Agent instructions
        tools=bing.definitions,  # Add Bing tool definitions
        headers={"x-ms-enable-preview": "true"}  # Enable preview features
    )
    print(f"Created agent, ID: {agent.id}")  # Print agent ID

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")  # Print thread ID

    # Create message to thread with user input
    message = project_client.agents.create_message(
        thread_id=thread.id,  # Thread ID
        role="user",  # Message role
        content=input("Enter your query: "),  # User input as message content
        # content="what is weather of Mumabi today?",  # Example static content
    )
    print(f"Created message, ID: {message.id}")  # Print message ID

    # Create and process agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")  # Print run status

    # Retrieve run step details to get Bing Search query link
    # To render the webpage, replace endpoint of Bing search query URLs with `www.bing.com`.
    run_steps = project_client.agents.list_run_steps(run_id=run.id, thread_id=thread.id)
    run_steps_data = run_steps['data']  # Get run steps data
    # print(f"Last run step detail: {run_steps_data}")  # Optionally print run step details

    if run.status == "failed":  # If run failed, print error
        print(f"Run failed: {run.last_error}")

    # Delete the assistant when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")  # Print deletion confirmation

    # Fetch and log all messages in chronological order
    messages_response = project_client.agents.list_messages(thread_id=thread.id)
    messages_data = messages_response["data"]  # Get messages data

    # Sort messages by creation time (ascending)
    sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

    print("\n--- Thread Messages ---")  # Print header
    for msg in sorted_messages:
        role = msg["role"].upper()  # Get message role
        # Each 'content' is a list; get the first text block if present
        content_blocks = msg.get("content", [])
        text_value = ""
        if content_blocks and content_blocks[0]["type"] == "text":
            text_value = content_blocks[0]["text"]["value"]  # Extract text value
        print(f"{role}: {text_value}")  # Print role and message content

#
# ---
#
# Explanation for Participants:
#
# This script demonstrates how to use Azure AI Foundry to build an AI agent that leverages Bing Search as a tool.
# Steps:
# 1. Loads environment variables for secure credentials and connection info.
# 2. Initializes the Azure AI Project client and retrieves a Bing connection.
# 3. Sets up a Bing search tool for the agent.
# 4. Creates an agent using GPT-4 and attaches the Bing tool.
# 5. Starts a new conversation thread and sends a user query.
# 6. Processes the agent's run, retrieves results, and prints all messages in order.
# 7. Cleans up by deleting the agent after use.
#
# This workflow is foundational for building intelligent assistants that can search the web and respond to user queries using Azure AI Foundry.