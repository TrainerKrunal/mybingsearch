
# Import required modules
import os  # For environment variables
import json  # For JSON serialization
from azure.ai.projects import AIProjectClient  # Azure AI Foundry project client
from azure.identity import DefaultAzureCredential  # Azure authentication
from azure.ai.projects.models import BingGroundingTool, FunctionTool, ToolSet  # Tools for agent
from user_functions import user_functions  # Import user-defined functions

from dotenv import load_dotenv
load_dotenv()

# Initialize the Azure AI Project Client using credentials and connection string
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),  # Use default Azure credentials
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],  # Connection string from environment
)

# Retrieve Bing connection ID from Azure AI Foundry
bing_connection = project_client.connections.get(
    connection_name=os.environ["BING_CONNECTION"]  # Bing connection name from environment
)
conn_id = bing_connection.id  # Get the connection ID

# Initialize Bing grounding tool with the connection ID
bing = BingGroundingTool(connection_id=conn_id)

# Initialize function tool with user-defined functions
functions = FunctionTool(functions=user_functions)

# Combine Bing and function tools into a toolset
toolset = ToolSet()
toolset.add(bing)  # Add Bing tool
toolset.add(functions)  # Add user function tool

# Create the agent with the combined toolset
with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4",  # Use GPT-4 model
        name="ai-agent-demo",  # Name of the agent
        instructions="You are a helpful assistant that performs web searches and calculations, choosing the appropriate tool based on the query.",  # Agent instructions
        toolset=toolset,  # Attach toolset
        headers={"x-ms-enable-preview": "true"}  # Enable preview features
    )
    print(f"Created agent, ID: {agent.id}")  # Print agent ID

    # Create a communication thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")  # Print thread ID

    # User's message (input from user)
    # user_input = "what is weather of Mumabi today?"  # Example static input
    # user_input = "calculate 2 ** 2"  # Example calculation
    user_input = input("Enter your query: ")  # Get user input
    message = project_client.agents.create_message(
        thread_id=thread.id,  # Thread ID
        role="user",  # Message role
        content=user_input,  # User's query
    )
    print(f"Created message, ID: {message.id}")  # Print message ID

    # Process the agent run (execute the agent)
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")  # Print run status

    if run.status == "failed":  # If run failed, print error
        print(f"Run failed: {run.last_error}")

    # Retrieve and display messages in chronological order
    messages_response = project_client.agents.list_messages(thread_id=thread.id)
    messages_data = messages_response["data"]  # Get messages data
    sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])  # Sort by creation time

    print("\n--- Thread Messages (sorted) ---")  # Print header
    for msg in sorted_messages:
        role = msg["role"].upper()  # Get message role
        content_blocks = msg.get("content", [])  # Get content blocks
        text_value = ""
        if content_blocks and content_blocks[0]["type"] == "text":
            text_value = content_blocks[0]["text"]["value"]  # Extract text value
        print(f"{role}: {text_value}")  # Print role and message content

    # Delete the agent after completion
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")  # Print deletion confirmation

#
# ---
#
# Explanation for Participants:
#
# This script demonstrates how to build an Azure AI Foundry agent that can both search the web (using Bing) and perform calculations (using user-defined functions).
# Steps:
# 1. Loads environment variables for secure credentials and connection info.
# 2. Initializes the Azure AI Project client and retrieves a Bing connection.
# 3. Sets up Bing and custom function tools, then combines them into a toolset.
# 4. Creates an agent using GPT-4 and attaches the toolset.
# 5. Starts a new conversation thread and sends a user query (which can be a search or a calculation).
# 6. Processes the agent's run, retrieves results, and prints all messages in order.
# 7. Cleans up by deleting the agent after use.
#
# This workflow is foundational for building intelligent assistants that can both search the web and perform custom logic using Azure AI Foundry.
