from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_client_membership(search: str) -> dict:
    """Get membership details of a specific client by name or ID.

    Args:
        search: Client name or ID to search for

    Use this tool when user asks about:
    - Membership details of a client
    - Client's plan/subscription info
    - When does membership expire
    - Membership status of a member
    """
    client = get_api_client()
    try:
        # First search for the client
        users_response = await client.get("/users", {"role": "client", "search": search, "limit": 5})

        if not users_response or "data" not in users_response:
            return {"error": "Client not found"}

        users = users_response.get("data", [])
        if not users:
            return {"error": f"No client found matching '{search}'"}

        # Get the first matching client
        user = users[0]
        user_id = user.get("id")

        # Get memberships for this client
        memberships_response = await client.get("/memberships", {"clientId": user_id, "limit": 5})

        return {
            "client": {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
            },
            "memberships": memberships_response.get("data", []) if memberships_response else []
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_membership_stats() -> dict:
    """Get membership statistics including active, expired, and expiring soon counts.

    Use this tool when user asks about:
    - How many active memberships
    - Membership statistics
    - Expired memberships count
    """
    client = get_api_client()
    try:
        response = await client.get("/memberships/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
