import logging
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from config import config
from prompts import SYSTEM_PROMPT
from tools import ALL_TOOLS, TOOL_MAP, set_api_client
from auth import TenantContext

logger = logging.getLogger(__name__)

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
    branch_id: int = None,
) -> dict:
    """Process a chat message and return response"""

    # Set API client with user's token and branch
    # Fall back to JWT's branchId if frontend doesn't send one
    effective_branch_id = branch_id if branch_id is not None else tenant.branch_id
    set_api_client(token, effective_branch_id)

    # Get or create conversation
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in conversations:
        conversations[conversation_id] = []

    conversation = conversations[conversation_id]

    # Build messages
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history (last 20 messages for context)
    for msg in conversation[-20:]:
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
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get LLM response
        response = await llm.ainvoke(messages)
        messages.append(response)
        conversation.append(response)

        # If no tool calls, we're done
        if not response.tool_calls:
            break

        # Process tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tools_used.append(tool_name)

            if tool_name in TOOL_MAP:
                try:
                    result = await TOOL_MAP[tool_name].ainvoke(tool_args)
                    tool_result = str(result)
                except Exception as e:
                    logger.error("Tool %s failed: %s", tool_name, e)
                    tool_result = f"Error executing tool: {str(e)}"
            else:
                tool_result = f"Unknown tool: {tool_name}"

            tool_message = ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
            )
            messages.append(tool_message)
            conversation.append(tool_message)

    # Get final response text
    final_response = response.content if response.content else "I couldn't process that request. Please try again."

    # Limit conversation history size
    if len(conversations[conversation_id]) > 40:
        conversations[conversation_id] = conversations[conversation_id][-40:]

    logger.info(
        "Chat processed: conversation=%s, tools=%s",
        conversation_id,
        tools_used,
    )

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
