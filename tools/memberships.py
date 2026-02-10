from langchain_core.tools import tool
from .base import get_api_client, extract_list


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
    - What plan is client on
    - Client's subscription information
    """
    client = get_api_client()
    try:
        # First search for the client to get their ID
        users_response = await client.get("/users", {"role": "client", "search": search, "limit": 5})

        if not users_response:
            return {"error": "Client not found"}

        users = extract_list(users_response)
        if not users:
            return {"error": f"No client found matching '{search}'"}

        # Get the first matching client
        user = users[0]
        user_id = user.get("id")

        if not user_id:
            return {"error": "Could not find client ID"}

        # Get full client details with membership info using the updated endpoint
        client_response = await client.get(f"/users/{user_id}")

        if not client_response:
            return {"error": "Could not fetch client details"}

        # Return formatted response with membership data
        active_membership = client_response.get("activeMembership")

        return {
            "client": {
                "id": client_response.get("id"),
                "name": client_response.get("name"),
                "email": client_response.get("email"),
                "phone": client_response.get("phone"),
                "status": client_response.get("status"),
            },
            "activeMembership": active_membership,
            "membershipId": active_membership.get("id") if active_membership else None,
            "membershipHistory": client_response.get("membershipHistory", []),
            "hasMembership": active_membership is not None
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


@tool
async def get_active_membership_clients() -> dict:
    """Get list of all clients who have active memberships.

    Use this tool when user asks about:
    - Which clients have active memberships
    - List clients with memberships
    - Who has active subscriptions
    - Active membership clients
    - Members with current plans

    Returns list of clients with their membership details.
    """
    client = get_api_client()
    try:
        response = await client.get("/memberships", {"status": "active", "limit": 50})

        if not response:
            return {"error": "Could not fetch memberships"}

        memberships = extract_list(response)

        # Format the response with client names and membership info
        clients_with_memberships = []
        for m in memberships:
            user = m.get("user", {})
            plan = m.get("plan", {})
            clients_with_memberships.append({
                "clientId": user.get("id"),
                "clientName": user.get("name"),
                "clientEmail": user.get("email"),
                "planName": plan.get("name"),
                "startDate": m.get("startDate"),
                "endDate": m.get("endDate"),
                "status": m.get("status"),
                "paymentStatus": m.get("paymentStatus"),
            })

        return {
            "count": len(clients_with_memberships),
            "clients": clients_with_memberships
        }
    except Exception as e:
        return {"error": str(e)}
