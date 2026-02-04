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
        response = await client.get("/dashboard/admin")

        # Extract client stats if available
        if isinstance(response, dict):
            total = response.get("totalClients", 0)
            active = response.get("activeClients", 0)
            inactive = response.get("inactiveClients", 0)

            if total == 0:
                return {
                    "totalClients": 0,
                    "activeClients": 0,
                    "inactiveClients": 0,
                    "message": "No clients found. The gym has no registered clients yet."
                }

            return response

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

        # Extract data properly
        clients = response.get("data", response) if isinstance(response, dict) else response
        clients_list = clients if isinstance(clients, list) else []

        if len(clients_list) == 0:
            return {
                "count": 0,
                "clients": [],
                "message": "No clients found. The gym has no registered clients yet."
            }

        # Return structured response with actual client names
        return {
            "count": len(clients_list),
            "clients": [{"id": c.get("id"), "name": c.get("name"), "email": c.get("email"), "status": c.get("status")} for c in clients_list]
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_client_details(search: str) -> dict:
    """Get details of a specific client by name or ID.

    Args:
        search: Client name or ID to search for

    Use this tool when user asks about:
    - Details of a specific client
    - Show me client X information
    - Get info about member named Y
    """
    client = get_api_client()
    try:
        response = await client.get("/users", {"role": "client", "search": search, "limit": 5})
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_client_by_id(client_id: int) -> dict:
    """Get full details of a specific client by their user ID, including membership information.

    Args:
        client_id: The user ID of the client

    Use this tool when:
    - You already know the client's ID and need their full details
    - User asks for membership details of a specific client
    - User asks about a client's subscription/plan information
    - You need to check if a client has an active membership

    Returns client data with:
    - Basic info (name, email, phone, status)
    - Active membership details (plan, dates, payment status, days remaining)
    - Membership history
    """
    client = get_api_client()
    try:
        response = await client.get(f"/users/{client_id}")
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
