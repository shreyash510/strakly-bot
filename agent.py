import json
import logging
import time
import uuid
from typing import AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from config import config
from prompts import SYSTEM_PROMPT
from tools import ALL_TOOLS, TOOL_MAP, set_api_client, cleanup_api_client
from auth import TenantContext

logger = logging.getLogger(__name__)

# In-memory conversation store (temporary per session)
# Each entry stores (messages_list, last_accessed_timestamp)
conversations: dict[str, tuple[list, float]] = {}

# Evict conversations older than 30 minutes
_CONVERSATION_TTL = 30 * 60

# Reusable LLM client for suggestion generation
_suggestion_llm = ChatOpenAI(
    model=config.OPENAI_MODEL,
    temperature=0.7,
    max_tokens=300,
    api_key=config.OPENAI_API_KEY,
    request_timeout=15,
)


def _evict_stale_conversations():
    """Remove conversations not accessed in the last 30 minutes."""
    now = time.time()
    stale = [cid for cid, (_, ts) in conversations.items() if now - ts > _CONVERSATION_TTL]
    for cid in stale:
        del conversations[cid]
    if stale:
        logger.info("Evicted %d stale conversations", len(stale))


def _setup_chat(
    message: str,
    token: str,
    tenant: TenantContext,
    conversation_id: str = None,
    branch_id: int = None,
) -> tuple[str, list, list, object]:
    """Common setup for both streaming and non-streaming chat."""
    _evict_stale_conversations()

    effective_branch_id = branch_id if branch_id is not None else tenant.branch_id
    set_api_client(token, effective_branch_id)

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in conversations:
        conversations[conversation_id] = ([], time.time())

    conv_messages, _ = conversations[conversation_id]
    conversations[conversation_id] = (conv_messages, time.time())

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in conv_messages[-20:]:
        messages.append(msg)

    user_message = HumanMessage(content=message)
    messages.append(user_message)
    conv_messages.append(user_message)

    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0,
        api_key=config.OPENAI_API_KEY,
        request_timeout=60,
    ).bind_tools(ALL_TOOLS)

    return conversation_id, conv_messages, messages, llm


async def _execute_tool_calls(tool_calls: list, messages: list, conversation: list) -> list[str]:
    """Execute tool calls and append results to messages. Returns tool names used."""
    tools_used = []
    for tool_call in tool_calls:
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

    return tools_used


def _trim_conversation(conversation_id: str):
    """Limit conversation history size."""
    entry = conversations.get(conversation_id)
    if entry and len(entry[0]) > 40:
        conversations[conversation_id] = (entry[0][-40:], entry[1])


def _strip_html(text: str) -> str:
    """Remove HTML tags from text for suggestion generation."""
    import re
    return re.sub(r'<[^>]+>', ' ', text).strip()


async def _generate_suggestions(user_message: str, assistant_response: str) -> list[str]:
    """Generate 3 follow-up question suggestions based on the conversation."""
    try:
        clean_response = _strip_html(assistant_response)[:800]
        prompt = (
            "You are a gym management assistant. The user just had this conversation with you.\n\n"
            f"USER: {user_message}\n"
            f"ASSISTANT: {clean_response}\n\n"
            "Based on EXACTLY what was discussed above, suggest 3 natural follow-up questions "
            "the user would likely ask next. The questions must be:\n"
            "- Directly related to the topic/data just discussed (NOT generic gym questions)\n"
            "- Short (under 40 characters each)\n"
            "- Actionable and specific\n\n"
            "For example:\n"
            "- If you showed client count → 'List all active clients', 'Expired memberships', 'New clients this month'\n"
            "- If you showed revenue → 'Revenue last month', 'Pending payments', 'Top paying clients'\n"
            "- If you showed attendance → 'Who came today?', 'Weekly attendance trend', 'Most active clients'\n"
            "- If you showed a client profile → 'Update their phone', 'Renew membership', 'Payment history'\n\n"
            "Return ONLY a JSON array of 3 strings. No explanation, no markdown, just the array."
        )
        result = await _suggestion_llm.ainvoke([HumanMessage(content=prompt)])
        # Strip markdown code fences if present
        content = result.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        questions = json.loads(content)
        if isinstance(questions, list):
            return [q for q in questions[:3] if isinstance(q, str) and len(q) <= 50]
    except Exception as e:
        logger.warning("Failed to generate suggestions: %s", e)
    return []


async def process_chat(
    message: str,
    token: str,
    tenant: TenantContext,
    conversation_id: str = None,
    branch_id: int = None,
) -> dict:
    """Process a chat message and return full response (non-streaming)."""
    conversation_id, conversation, messages, llm = _setup_chat(
        message, token, tenant, conversation_id, branch_id
    )

    tools_used = []
    max_iterations = 10

    for _ in range(max_iterations):
        response = await llm.ainvoke(messages)
        messages.append(response)
        conversation.append(response)

        if not response.tool_calls:
            break

        names = await _execute_tool_calls(response.tool_calls, messages, conversation)
        tools_used.extend(names)

    final_response = response.content if response.content else "I couldn't process that request. Please try again."
    _trim_conversation(conversation_id)
    await cleanup_api_client()

    suggested_questions = await _generate_suggestions(message, final_response)

    logger.info("Chat processed: conversation=%s, tools=%s", conversation_id, tools_used)

    return {
        "success": True,
        "response": final_response,
        "conversation_id": conversation_id,
        "tools_used": list(set(tools_used)),
        "suggested_questions": suggested_questions,
    }


async def process_chat_stream(
    message: str,
    token: str,
    tenant: TenantContext,
    conversation_id: str = None,
    branch_id: int = None,
) -> AsyncGenerator[str, None]:
    """Process a chat message and stream the final response as SSE events.

    Tool-calling iterations use ainvoke (non-streaming).
    The final text response uses astream for real token-by-token streaming.
    """
    conversation_id, conversation, messages, llm = _setup_chat(
        message, token, tenant, conversation_id, branch_id
    )

    # Send conversation_id immediately so frontend can track it
    yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"

    tools_used = []
    max_iterations = 10

    for _ in range(max_iterations):
        # Try streaming — collect chunks to detect tool calls vs content
        full_response = None
        has_content = False
        has_tool_calls = False

        async for chunk in llm.astream(messages):
            # Accumulate chunks into full response
            if full_response is None:
                full_response = chunk
            else:
                full_response = full_response + chunk

            # Stream content tokens immediately (OpenAI never mixes content + tool_calls)
            if chunk.content:
                has_content = True
                yield f"data: {json.dumps({'token': chunk.content})}\n\n"

            if chunk.tool_call_chunks:
                has_tool_calls = True

        if full_response is None:
            break

        messages.append(full_response)
        conversation.append(full_response)

        # If this was a content-only response, we're done (tokens already streamed)
        if has_content and not has_tool_calls:
            break

        # If tool calls, execute them and continue the loop
        if full_response.tool_calls:
            names = await _execute_tool_calls(full_response.tool_calls, messages, conversation)
            tools_used.extend(names)
            # Notify frontend that tools are being processed
            yield f"data: {json.dumps({'tools_used': names})}\n\n"
        else:
            # No content and no tool calls — edge case, bail out
            break

    _trim_conversation(conversation_id)
    await cleanup_api_client()
    logger.info("Chat streamed: conversation=%s, tools=%s", conversation_id, tools_used)

    # Generate and send suggested follow-up questions
    final_text = full_response.content if full_response and full_response.content else ""
    suggested_questions = await _generate_suggestions(message, final_text)
    if suggested_questions:
        yield f"data: {json.dumps({'suggested_questions': suggested_questions})}\n\n"

    yield "data: [DONE]\n\n"


def clear_conversation(conversation_id: str):
    """Clear a conversation from memory."""
    conversations.pop(conversation_id, None)
