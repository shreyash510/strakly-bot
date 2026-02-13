import logging
import time

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models import ChatRequest, ChatResponse, HealthResponse, PublicChatRequest
from auth import decode_token
from agent import process_chat, process_chat_stream, clear_conversation
from public_agent import process_public_chat, process_public_chat_stream, clear_public_conversation
from config import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Strakly Bot",
    description="AI-powered chatbot for Strakly gym management platform",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
def root():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/chat")
async def chat(
    request_body: ChatRequest,
    raw_request: Request,
    authorization: str = Header(..., description="Bearer token"),
):
    """
    Chat endpoint for AI assistant.
    Supports both JSON and SSE streaming responses based on Accept header.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    token = authorization.removeprefix("Bearer ")
    tenant = decode_token(token)
    logger.info("Chat request from user=%s gym=%s", tenant.user_id, tenant.gym_id)

    accept = raw_request.headers.get("accept", "")

    # Streaming SSE response
    if "text/event-stream" in accept:
        return StreamingResponse(
            process_chat_stream(
                message=request_body.message,
                token=token,
                tenant=tenant,
                conversation_id=request_body.conversation_id,
                branch_id=request_body.branch_id,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Regular JSON response
    result = await process_chat(
        message=request_body.message,
        token=token,
        tenant=tenant,
        conversation_id=request_body.conversation_id,
        branch_id=request_body.branch_id,
    )

    return ChatResponse(
        success=result["success"],
        response=result["response"],
        conversation_id=result["conversation_id"],
        tools_used=result["tools_used"],
        suggested_questions=result.get("suggested_questions", []),
    )


@app.delete("/chat/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    authorization: str = Header(..., description="Bearer token"),
):
    """Clear conversation history"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    clear_conversation(conversation_id)
    return {"success": True, "message": "Conversation cleared"}


# ── Public chatbot (no JWT, docs-only) ───────────────────────────

# Simple in-memory IP rate limiter
_rate_store: dict[str, list[float]] = {}


def _check_rate_limit(ip: str):
    """Raise 429 if IP exceeds config.PUBLIC_RATE_LIMIT in config.PUBLIC_RATE_WINDOW seconds."""
    now = time.time()
    window = config.PUBLIC_RATE_WINDOW
    limit = config.PUBLIC_RATE_LIMIT

    timestamps = _rate_store.get(ip, [])
    # Prune old entries
    timestamps = [t for t in timestamps if now - t < window]
    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many messages. Please wait a moment and try again.",
        )
    timestamps.append(now)
    _rate_store[ip] = timestamps


@app.post("/chat/public")
async def public_chat(request_body: PublicChatRequest, raw_request: Request):
    """Public chatbot endpoint — no authentication required. Docs/FAQ only."""
    client_ip = raw_request.client.host if raw_request.client else "unknown"
    _check_rate_limit(client_ip)

    logger.info("Public chat request from ip=%s", client_ip)

    accept = raw_request.headers.get("accept", "")

    if "text/event-stream" in accept:
        return StreamingResponse(
            process_public_chat_stream(
                message=request_body.message,
                conversation_id=request_body.conversation_id,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    result = await process_public_chat(
        message=request_body.message,
        conversation_id=request_body.conversation_id,
    )

    return ChatResponse(
        success=result["success"],
        response=result["response"],
        conversation_id=result["conversation_id"],
        tools_used=[],
        suggested_questions=result.get("suggested_questions", []),
    )


@app.delete("/chat/public/{conversation_id}")
async def delete_public_conversation(conversation_id: str):
    """Clear a public conversation."""
    clear_public_conversation(conversation_id)
    return {"success": True, "message": "Conversation cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
