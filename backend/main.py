from typing import List
from google.genai import types
import asyncio
from pathlib import Path
import logging
from clients.gemini_mpc_client import GeminiMCPClient
import os 
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.INFO)


# Get the parent directory of the current file
PARENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = PARENT_DIR.parent
SERVERS_DIR = "backend/servers"
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
async def process_query(request: QueryRequest):
    """API endpoint to process user queries"""
    try:
        system_instruction = '''
        You should provide accurate answer based on your general knowledge.

        Think-step-by-step and if the available tools can help you to answer the question, please use them at individual steps.
        '''
        
        mcp_servers = {
            "calculator": os.path.join(SERVERS_DIR, "calculator/mcp_server.py"),
            "keynote": os.path.join(SERVERS_DIR, "keynote/mcp_server.py"),
            "email": os.path.join(SERVERS_DIR, "email/mcp_server.py"),
        }
        
        response_content = await run_agent_loop(system_instruction, request.query, mcp_servers)
        
        # Extract text from the response content
        if response_content and hasattr(response_content, 'parts') and response_content.parts:
            response_text = response_content.parts[0].text
            return {"response": response_text}
        return {"response": "No response generated"}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process query: {str(e)}"}
        )

# Serve the frontend static files
@app.on_event("startup")
async def startup_event():
    if FRONTEND_DIR.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
    else:
        logger.warning(f"Frontend directory not found at {FRONTEND_DIR}. Frontend will not be served.")

async def run_agent_loop(system_instruction: str, initial_query: str, mcp_servers=None) -> types.Content:
    """
    Executes an agent loop that processes user queries, interacts with tools, and generates responses 
    using a model capable of function calling. The loop continues until a maximum number of tool turns 
    is reached or no further function calls are required.
    Args:
        system_prompt (str): The initial system prompt to guide the agent's behavior.
        initial_query (str): The user's initial query to start the interaction.
        mcp_servers (Optional[List[str]]): A list of MCP server addresses to connect to. Defaults to None.
    Returns:
        None
    """
    
    # Initialize the conversation with the user's initial query
    contents = [types.Content(role="user", parts=[types.Part(text=initial_query)])]
    
    # Create an instance of the Gemini MCP client and connect to the specified MCP servers
    mcp_client = GeminiMCPClient()
    await mcp_client.connect_to_multiple_servers(mcp_servers)

    # Retrieve tool schemas and define tools for function calling
    tools = types.Tool(function_declarations=mcp_client.get_tool_schemas())
    
    # Send the initial query to the model along with tool definitions
    response = await mcp_client.client.aio.models.generate_content(
        model=mcp_client.model,  # Or your preferred model supporting function calling
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0,  # Set temperature for response generation
            tools=[tools],  # Include tools for function calling
        ),  # Example other config
    )
    
    # Add the model's initial response to the conversation history
    contents.append(response.candidates[0].content)
    
    # --- Tool Calling Loop ---            
    turn_count = 0
    max_tool_turns = 5  # Define the maximum number of tool interaction turns

    # Loop to process function calls and generate responses
    while response.function_calls and turn_count < max_tool_turns:
        turn_count += 1
        tool_response_parts: List[types.Part] = []

        # --- 4.1 Process all function calls in order and return in this turn ---
        for fc_part in response.function_calls:
            tool_name = fc_part.name  # Extract the tool name
            args = fc_part.args or {}  # Ensure arguments are a dictionary
            logger.info(f"Attempting to call MCP tool: '{tool_name}' with args: {args}")

            try:
                # Execute the tool using the MCP client
                tool_result = await mcp_client.execute_tool(fc_part)
                if tool_result.isError:
                    # Handle tool execution errors
                    tool_response = {"error": tool_result.content[0].text}
                    logger.info(f"MCP tool '{tool_name}' execution failed: {tool_result.content[0].text}")
                else:
                    # Handle successful tool execution
                    tool_response = {"result": tool_result.content[0].text}
                logger.info(f"MCP tool '{tool_name}' execution completed")
            except Exception as e:
                # Handle exceptions during tool execution
                tool_response = {"error":  f"Tool execution failed: {type(e).__name__}: {e}"}
            
            # Prepare a FunctionResponse part for the tool's output
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name, response=tool_response
                )
            )

        # Append the tool responses to the conversation history
        contents.append(types.Content(role="user", parts=tool_response_parts))
        logger.info(f"Added {len(tool_response_parts)} tool response parts to history.")

        # Update the conversation history with the tool responses
        logger.info("Making subsequent API call with tool responses...")
        # Send the updated conversation history to the model
        response = await mcp_client.client.aio.models.generate_content(
            model=mcp_client.model,
            contents=contents,  # Send updated history
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=1.0,  # Adjust temperature for subsequent calls
                tools=[tools],  # Keep sending the same tools
            ),  # Keep sending same config
        )
        # Append the model's response to the conversation history
        contents.append(response.candidates[0].content)

    # Check if the maximum number of tool turns has been reached
    if turn_count >= max_tool_turns and response.function_calls:
        logger.warn(f"Maximum tool turns ({max_tool_turns}) reached. Exiting loop.")

    logger.info("Execution completed")
    if response and hasattr(response, 'candidates') and response.candidates:
        return response.candidates[0].content
    return None


if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


