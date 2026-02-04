from langchain_core.tools import tool
from .base import get_api_client


@tool
async def get_clients_stats() -> dict:
    """Get statistics about clients/members including total count, active, inactive, and new members this month.

    Use this tool when user asks about:
    - How many members/clients do I have?
    - Member statistics
    - Active vs inactive members
    - New member count
    """
    client = get_api_client()
    try:
        response = await client.get("/clients/stats")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_clients_list(
    status: str = None,
    search: str = None,
    limit: int = 10,
) -> dict:
    """Get list of clients/members with optional filters.

    Use this tool when user asks about:
    - List of members
    - Search for a specific member
    - Members with specific status

    Args:
        status: Filter by status (active, inactive, expired)
        search: Search by name or email
        limit: Maximum number of results (default 10)
    """
    client = get_api_client()
    params = {"limit": limit}
    if status:
        params["status"] = status
    if search:
        params["search"] = search

    try:
        response = await client.get("/clients", params)
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_expiring_memberships(days: int = 7) -> dict:
    """Get list of memberships that are expiring soon.

    Use this tool when user asks about:
    - Expiring memberships
    - Members whose subscription is ending
    - Renewals needed

    Args:
        days: Number of days to look ahead (default 7)
    """
    client = get_api_client()
    try:
        response = await client.get("/memberships/expiring", {"days": days})
        return response
    except Exception as e:
        return {"error": str(e)}
