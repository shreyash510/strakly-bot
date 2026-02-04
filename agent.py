from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import config
from prompts import SYSTEM_PROMPT
from tools import (
    set_api_client,
    get_clients_stats,
    get_clients_list,
    get_client_details,
    get_expiring_memberships,
    get_attendance_today,
    get_attendance_stats,
    get_revenue_stats,
    get_membership_sales,
    get_trainers_list,
    get_trainers_stats,
    get_enquiries_list,
    get_enquiries_stats,
    get_gym_info,
    get_branches_info,
)
from auth import TenantContext
import uuid

# All available tools
ALL_TOOLS = [
    get_clients_stats,
    get_clients_list,
    get_client_details,
    get_expiring_memberships,
    get_attendance_today,
    get_attendance_stats,
    get_revenue_stats,
    get_membership_sales,
    get_trainers_list,
    get_trainers_stats,
    get_enquiries_list,
    get_enquiries_stats,
    get_gym_info,
    get_branches_info,
]

# Tool name to function mapping
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

# In-memory conversation store (temporary per session)
conversations: dict[str, list] = {}


def get_llm_with_tools():
    """Create LLM instance with tools bound"""
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0,
        api_key=config.OPENAI_API_KEY,
    )
    return llm.bind_tools(ALL_TOOLS)


async def process_chat(
    message: str,
    token: str,
    tenant: TenantContext,
    conversation_id: str = None,
) -> dict:
    """Process a chat message and return response"""

    # Set API client with user's token
    set_api_client(token)

    # Get or create conversation
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversation = conversations[conversation_id]

    # Build messages
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history (last 10 messages for context)
    for msg in conversation[-10:]:
        messages.append(msg)

    # Add current user message
    user_message = HumanMessage(content=message)
    messages.append(user_message)
    conversation.append(user_message)

    # Get LLM with tools
    llm = get_llm_with_tools()

    # Track tools used
    tools_used = []

    # Agent loop - process until no more tool calls
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get LLM response
        response = await llm.ainvoke(messages)
        messages.append(response)

        # If no tool calls, we're done
        if not response.tool_calls:
            break

        # Process tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tools_used.append(tool_name)

            # Get and execute tool
            if tool_name in TOOL_MAP:
                try:
                    tool_fn = TOOL_MAP[tool_name]
                    result = await tool_fn.ainvoke(tool_args)
                    tool_result = str(result)
                except Exception as e:
                    tool_result = f"Error executing tool: {str(e)}"
            else:
                tool_result = f"Unknown tool: {tool_name}"

            # Add tool result to messages
            tool_message = ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
            )
            messages.append(tool_message)

    # Get final response text
    final_response = response.content if response.content else "I couldn't process that request. Please try again."

    # Save assistant response to conversation
    conversation.append(AIMessage(content=final_response))

    # Limit conversation history size
    if len(conversations[conversation_id]) > 20:
        conversations[conversation_id] = conversations[conversation_id][-20:]

    return {
        "success": True,
        "response": final_response,
        "conversation_id": conversation_id,
        "tools_used": list(set(tools_used)),
    }


def clear_conversation(conversation_id: str):
    """Clear a conversation from memory"""
    if conversation_id in conversations:
        del conversations[conversation_id]
