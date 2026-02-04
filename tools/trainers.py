from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_trainers_list() -> dict:
    """Get list of trainers.

    Use this tool when user asks about:
    - List of trainers
    - How many trainers do I have?
    - Trainer information
    """
    client = get_api_client()
    try:
        response = await client.get("/users", {"role": "trainer", "limit": 20})
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
        # Get dashboard which includes trainer stats
        response = await client.get("/dashboard/admin")
        return response
    except Exception as e:
        return {"error": str(e)}
