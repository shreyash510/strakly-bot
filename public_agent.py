import json
import logging
import time
import uuid
from typing import AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import config
from prompts.public_prompt import PUBLIC_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# In-memory conversation store
public_conversations: dict[str, tuple[list, float]] = {}
_CONVERSATION_TTL = 30 * 60  # 30 minutes

# Reusable LLM for suggestions
_suggestion_llm = ChatOpenAI(
    model=config.OPENAI_MODEL,
    temperature=0.7,
    max_tokens=300,
    api_key=config.OPENAI_API_KEY,
    request_timeout=15,
)


def _evict_stale():
    now = time.time()
    stale = [cid for cid, (_, ts) in public_conversations.items() if now - ts > _CONVERSATION_TTL]
    for cid in stale:
        del public_conversations[cid]


async def _generate_suggestions(user_message: str, assistant_response: str) -> list[str]:
    try:
        clean = assistant_response[:800]
        prompt = (
            "You are a gym management software assistant on a public website.\n\n"
            f"USER: {user_message}\nASSISTANT: {clean}\n\n"
            "Suggest 3 short follow-up questions (under 40 chars each) the visitor would likely ask next. "
            "Questions should be about Strakly features, pricing, or setup. "
            "Return ONLY a JSON array of 3 strings."
        )
        result = await _suggestion_llm.ainvoke([HumanMessage(content=prompt)])
        content = result.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        questions = json.loads(content)
        if isinstance(questions, list):
            return [q for q in questions[:3] if isinstance(q, str) and len(q) <= 50]
    except Exception as e:
        logger.warning("Failed to generate public suggestions: %s", e)
    return []


async def process_public_chat(message: str, conversation_id: str = None) -> dict:
    _evict_stale()

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in public_conversations:
        public_conversations[conversation_id] = ([], time.time())

    conv_messages, _ = public_conversations[conversation_id]
    public_conversations[conversation_id] = (conv_messages, time.time())

    recent = conv_messages[-20:]
    messages = [SystemMessage(content=PUBLIC_SYSTEM_PROMPT)]
    messages.extend(recent)

    user_msg = HumanMessage(content=message)
    messages.append(user_msg)
    conv_messages.append(user_msg)

    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0.3,
        api_key=config.OPENAI_API_KEY,
        request_timeout=60,
    )

    response = await llm.ainvoke(messages)
    conv_messages.append(response)

    # Trim if too long
    if len(conv_messages) > 40:
        public_conversations[conversation_id] = (conv_messages[-40:], time.time())

    final_response = response.content or "I'm sorry, I couldn't process that. Please try again."
    suggested = await _generate_suggestions(message, final_response)

    return {
        "success": True,
        "response": final_response,
        "conversation_id": conversation_id,
        "suggested_questions": suggested,
    }


async def process_public_chat_stream(message: str, conversation_id: str = None) -> AsyncGenerator[str, None]:
    _evict_stale()

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in public_conversations:
        public_conversations[conversation_id] = ([], time.time())

    conv_messages, _ = public_conversations[conversation_id]
    public_conversations[conversation_id] = (conv_messages, time.time())

    recent = conv_messages[-20:]
    messages = [SystemMessage(content=PUBLIC_SYSTEM_PROMPT)]
    messages.extend(recent)

    user_msg = HumanMessage(content=message)
    messages.append(user_msg)
    conv_messages.append(user_msg)

    yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"

    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        temperature=0.3,
        api_key=config.OPENAI_API_KEY,
        request_timeout=60,
    )

    full_response = None
    async for chunk in llm.astream(messages):
        if full_response is None:
            full_response = chunk
        else:
            full_response = full_response + chunk
        if chunk.content:
            yield f"data: {json.dumps({'token': chunk.content})}\n\n"

    if full_response:
        conv_messages.append(full_response)

    if len(conv_messages) > 40:
        public_conversations[conversation_id] = (conv_messages[-40:], time.time())

    final_text = full_response.content if full_response and full_response.content else ""
    suggested = await _generate_suggestions(message, final_text)
    if suggested:
        yield f"data: {json.dumps({'suggested_questions': suggested})}\n\n"

    yield "data: [DONE]\n\n"


def clear_public_conversation(conversation_id: str):
    public_conversations.pop(conversation_id, None)
