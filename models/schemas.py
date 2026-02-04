from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    branch_id: Optional[int] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    conversation_id: str
    tools_used: list[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str
