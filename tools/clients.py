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
        # Use dashboard endpoint which includes client stats
        response = await client.get("/dashboard/admin")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_clients_list() -> dict:
    """Get list of clients/members.

    Use this tool when user asks about:
    - List of members
    - Show me all clients
    - Who are my members
    """
    client = get_api_client()
    try:
        response = await client.get("/users", {"role": "client", "limit": 20})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_expiring_memberships() -> dict:
    """Get list of memberships expiring in the next 7 days.

    Use this tool when user asks about:
    - Expiring memberships
    - Members whose subscription is ending
    - Renewals needed
    """
    client = get_api_client()
    try:
        response = await client.get("/memberships/expiring", {"days": 7})
        return response
    except Exception as e:
        return {"error": str(e)}
