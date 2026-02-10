from langchain_core.tools import tool
from .base import get_api_client, extract_paginated


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
        response = await client.get("/users", {"role": "trainer", "page": 1, "limit": 5})
        trainers, pagination = extract_paginated(response)

        if len(trainers) == 0:
            return {"count": 0, "trainers": [], "message": "No trainers found."}

        return {
            "count": pagination.get("total", len(trainers)),
            "totalPages": pagination.get("totalPages", 1),
            "page": 1,
            "trainers": [{"id": t.get("id"), "name": t.get("name"), "email": t.get("email"), "status": t.get("status")} for t in trainers],
            "endpoint": "/users",
            "filters": {"role": "trainer"},
        }
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
