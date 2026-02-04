from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_trainers_list(status: str = None, limit: int = 10) -> dict:
    """Get list of trainers.

    Use this tool when user asks about:
    - List of trainers
    - How many trainers do I have?
    - Trainer information

    Args:
        status: Filter by status (active, inactive)
        limit: Maximum number of results (default 10)
    """
    client = get_api_client()
    params = {"limit": limit}
    if status:
        params["status"] = status

    try:
        response = await client.get("/trainers", params)
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_trainers_stats() -> dict:
    """Get statistics about trainers.

    Use this tool when user asks about:
    - Trainer statistics
    - Total trainers count
    - Active trainers
    """
    client = get_api_client()
    try:
        response = await client.get("/trainers/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
