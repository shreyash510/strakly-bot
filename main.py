import logging

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models import ChatRequest, ChatResponse, HealthResponse
from auth import decode_token
from agent import process_chat, process_chat_stream, clear_conversation
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
