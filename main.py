import logging

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse, HealthResponse
from auth import decode_token
from agent import process_chat, clear_conversation
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
    allow_origins=["*"],  # Update with your frontend URLs in production
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


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str = Header(..., description="Bearer token"),
):
    """
    Chat endpoint for AI assistant.

    Send a message and receive an AI-generated response based on your gym data.
    """
    # Validate and decode token
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    # Extract token (remove 'Bearer ' prefix if present)
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:]

    # Decode and validate token
    tenant = decode_token(token)
    logger.info("Chat request from user=%s gym=%s", tenant.user_id, tenant.gym_id)

    # Process chat message
    result = await process_chat(
        message=request.message,
        token=token,
        tenant=tenant,
        conversation_id=request.conversation_id,
        branch_id=request.branch_id,
    )

    return ChatResponse(
        success=result["success"],
        response=result["response"],
        conversation_id=result["conversation_id"],
        tools_used=result["tools_used"],
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
