from langchain_core.tools import tool
from .base import get_api_client, extract_list


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
        response = await client.get("/users", {"role": "trainer", "noPagination": "true"})
        trainers = extract_list(response)

        if len(trainers) == 0:
            return {"count": 0, "trainers": [], "message": "No trainers found."}

        return {
            "count": len(trainers),
            "trainers": [{"id": t.get("id"), "name": t.get("name"), "email": t.get("email"), "status": t.get("status")} for t in trainers],
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
