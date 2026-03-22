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
        users_response = await client.get("/users", {"role": "client", "search": search, "noPagination": "true"})

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
        response = await client.get("/memberships", {"status": "active", "limit": 500})

        if not response:
            return {"error": "Could not fetch memberships"}

        memberships = extract_list(response)

        clients_with_memberships = []
        for m in memberships:
            user = m.get("user", {})
            plan = m.get("plan", {})
            clients_with_memberships.append({
                "clientId": user.get("id"),
                "clientName": user.get("name"),
                "clientEmail": user.get("email"),
                "planName": plan.get("name"),
                "status": m.get("status"),
            })

        return {
            "count": len(clients_with_memberships),
            "clients": clients_with_memberships,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def freeze_membership(membership_id: int, start_date: str, end_date: str, reason: str = None) -> dict:
    """Freeze/hold a membership for a specified period.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        membership_id: The membership ID (required)
        start_date: Freeze start date in YYYY-MM-DD format (required)
        end_date: Freeze end date in YYYY-MM-DD format (required)
        reason: Reason for freezing (optional)
    """
    client = get_api_client()
    try:
        data = {
            "startDate": start_date,
            "endDate": end_date,
        }
        if reason:
            data["reason"] = reason

        response = await client.post(f"/memberships/{membership_id}/freeze", data)
        return {
            "success": True,
            "message": f"Membership frozen from {start_date} to {end_date}",
            "freeze": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def unfreeze_membership(membership_id: int) -> dict:
    """Unfreeze/resume a currently frozen membership.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        membership_id: The membership ID (required)
    """
    client = get_api_client()
    try:
        response = await client.post(f"/memberships/{membership_id}/unfreeze", {})
        return {
            "success": True,
            "message": "Membership unfrozen successfully",
            "result": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def get_freeze_history(membership_id: int) -> dict:
    """Get freeze/hold history for a membership.

    Args:
        membership_id: The membership ID (required)

    Use this tool when user asks about:
    - Membership freeze history
    - How many times was membership frozen
    - Freeze records
    """
    client = get_api_client()
    try:
        response = await client.get(f"/memberships/{membership_id}/freezes")
        freezes = extract_list(response)

        if not freezes:
            return {"count": 0, "freezes": [], "message": "No freeze history for this membership."}

        return {
            "count": len(freezes),
            "freezes": [
                {
                    "id": f.get("id"),
                    "startDate": f.get("startDate"),
                    "endDate": f.get("endDate"),
                    "reason": f.get("reason"),
                    "status": f.get("status"),
                    "createdAt": f.get("createdAt"),
                }
                for f in freezes
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def renew_membership(user_id: int, plan_id: int, payment_method: str = "cash", start_date: str = "") -> str:
    """Renew a client's membership with a new plan. The new membership starts from the old one's end date.

    Use when: admin wants to renew a client's membership, extend subscription, re-enroll a client.

    Args:
        user_id: The client's user ID
        plan_id: The membership plan ID to renew with
        payment_method: Payment method (cash, card, upi, bank_transfer). Defaults to cash.
        start_date: Optional start date (YYYY-MM-DD). If empty, starts from current membership end date.
    """
    client = get_api_client()
    body = {"userId": user_id, "planId": plan_id, "paymentMethod": payment_method}
    if start_date:
        body["startDate"] = start_date
    return await client.post("/memberships/renew", body)
