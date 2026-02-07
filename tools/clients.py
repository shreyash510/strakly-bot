from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id
import secrets
import string


def generate_password(length: int = 12) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


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
            "clients": [{"id": c.get("id"), "name": c.get("name"), "email": c.get("email"), "status": c.get("status"), "avatar": c.get("avatar")} for c in clients_list]
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


@tool
async def create_client(
    name: str,
    email: str,
    phone: str = None,
    gender: str = None,
    address: str = None,
    city: str = None,
) -> dict:
    """Create a new client/member with the provided details.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Full name of the client (required)
        email: Email address (required)
        phone: Phone number (optional)
        gender: Gender - male, female, or other (optional)
        address: Address (optional)
        city: City (optional)

    Returns:
        Success response with created client details, or error message
    """
    client = get_api_client()
    try:
        # Generate a temporary password
        temp_password = generate_password()

        # Prepare the data
        data = {
            "name": name,
            "email": email,
            "password": temp_password,
            "role": "client",
            "status": "active",
        }

        # Add optional fields if provided
        if phone:
            data["phone"] = phone
        if gender and gender in ["male", "female", "other"]:
            data["gender"] = gender
        if address:
            data["address"] = address
        if city:
            data["city"] = city

        # Add branch ID if available from context
        branch_id = get_current_branch_id()
        if branch_id:
            data["branchIds"] = [branch_id]

        # Create the user via POST /users
        response = await client.post("/users", data)

        return {
            "success": True,
            "message": f"Client created successfully for {name}",
            "client": {
                "id": response.get("id"),
                "name": response.get("name"),
                "email": response.get("email"),
                "phone": response.get("phone"),
                "status": "active",
            },
            "temp_password": temp_password,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def bulk_create_clients(
    clients_json: str,
) -> dict:
    """Bulk create multiple clients/members at once.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        clients_json: JSON string containing array of client objects.
            Each object should have: name (required), email (required),
            and optionally: phone, gender, address, city.
            Example: '[{"name": "John", "email": "john@example.com", "phone": "1234567890"}, {"name": "Jane", "email": "jane@example.com"}]'

    Returns:
        Summary with success count, failed count, errors, and created clients list.
    """
    import json as json_module

    client = get_api_client()
    try:
        clients_list = json_module.loads(clients_json)

        if not isinstance(clients_list, list):
            return {"error": "Expected a JSON array of client objects", "success": False}

        if len(clients_list) == 0:
            return {"error": "No clients provided", "success": False}

        if len(clients_list) > 50:
            return {"error": "Maximum 50 clients allowed per batch", "success": False}

        # Prepare each client with required fields
        users = []
        for i, cl in enumerate(clients_list):
            if not cl.get("name") or not cl.get("email"):
                return {
                    "error": f"Client {i + 1}: name and email are required",
                    "success": False,
                }

            user_data = {
                "name": cl["name"],
                "email": cl["email"],
                "password": generate_password(),
                "role": "client",
                "status": "active",
            }

            if cl.get("phone"):
                user_data["phone"] = cl["phone"]
            if cl.get("gender") and cl["gender"] in ["male", "female", "other"]:
                user_data["gender"] = cl["gender"]
            if cl.get("address"):
                user_data["address"] = cl["address"]
            if cl.get("city"):
                user_data["city"] = cl["city"]

            branch_id = get_current_branch_id()
            if branch_id:
                user_data["branchIds"] = [branch_id]

            users.append(user_data)

        # Call bulk create endpoint
        response = await client.post("/users/bulk/create", {"users": users})

        return {
            "success": True,
            "message": f"Bulk client creation completed: {response.get('success', 0)} created, {response.get('failed', 0)} failed",
            "total_submitted": len(clients_list),
            "total_created": response.get("success", 0),
            "total_failed": response.get("failed", 0),
            "created": response.get("created", []),
            "errors": response.get("errors", []),
        }
    except json_module.JSONDecodeError:
        return {"error": "Invalid JSON format. Please provide a valid JSON array.", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def update_client(
    client_id: int,
    name: str = None,
    email: str = None,
    phone: str = None,
    status: str = None,
    gender: str = None,
    address: str = None,
    city: str = None,
    state: str = None,
    zip_code: str = None,
    date_of_birth: str = None,
) -> dict:
    """Update a client/member's details by their ID.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        client_id: The user ID of the client to update (required)
        name: New name (optional)
        email: New email (optional)
        phone: New phone number (optional)
        status: New status - must be one of: onboarding, confirm, active, expired, inactive, rejected, archive (optional)
        gender: New gender - male, female, other (optional)
        address: New address (optional)
        city: New city (optional)
        state: New state (optional)
        zip_code: New ZIP code (optional)
        date_of_birth: New date of birth as YYYY-MM-DD (optional)

    Returns:
        Updated client details or error message
    """
    client = get_api_client()
    try:
        data = {}
        if name is not None:
            data["name"] = name
        if email is not None:
            data["email"] = email
        if phone is not None:
            data["phone"] = phone
        if status is not None:
            data["status"] = status
        if gender is not None and gender in ["male", "female", "other"]:
            data["gender"] = gender
        if address is not None:
            data["address"] = address
        if city is not None:
            data["city"] = city
        if state is not None:
            data["state"] = state
        if zip_code is not None:
            data["zipCode"] = zip_code
        if date_of_birth is not None:
            data["dateOfBirth"] = date_of_birth

        if not data:
            return {"error": "No fields to update provided", "success": False}

        response = await client.patch(f"/users/{client_id}", data)

        return {
            "success": True,
            "message": f"Client {client_id} updated successfully.",
            "client": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def bulk_update_clients(
    client_ids_json: str,
    status: str = None,
    branch_ids_json: str = None,
) -> dict:
    """Bulk update multiple clients - change their status or branch assignments.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        client_ids_json: JSON string containing array of client IDs to update.
            Example: '[1, 2, 3, 4, 5]'
        status: New status to set for all clients - must be one of: onboarding, confirm, active, expired, inactive, rejected, archive (optional)
        branch_ids_json: JSON string containing array of branch IDs to assign.
            Example: '[1, 2]' (optional)

    Returns:
        Summary with update results.
    """
    import json as json_module

    client = get_api_client()
    try:
        client_ids = json_module.loads(client_ids_json)

        if not isinstance(client_ids, list) or len(client_ids) == 0:
            return {"error": "Expected a non-empty JSON array of client IDs", "success": False}

        try:
            client_ids = [int(cid) for cid in client_ids]
        except (ValueError, TypeError):
            return {"error": "All client IDs must be valid numbers", "success": False}

        data = {"userIds": client_ids}

        if status is not None:
            data["status"] = status

        if branch_ids_json is not None:
            branch_ids = json_module.loads(branch_ids_json)
            if isinstance(branch_ids, list):
                data["branchIds"] = [int(bid) for bid in branch_ids]

        if len(data) == 1:
            return {"error": "No update fields provided. Specify status or branch_ids_json.", "success": False}

        response = await client.patch("/users/bulk/update", data)

        return {
            "success": True,
            "message": f"Bulk update completed for {len(client_ids)} clients.",
            "details": response,
        }
    except json_module.JSONDecodeError:
        return {"error": "Invalid JSON format.", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def delete_client(client_id: int) -> dict:
    """Delete a single client/member by their ID.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        client_id: The user ID of the client to delete

    Returns:
        Success response or error message
    """
    client = get_api_client()
    try:
        response = await client.delete(f"/users/{client_id}")
        return {
            "success": True,
            "message": f"Client with ID {client_id} has been deleted successfully.",
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def bulk_delete_clients(client_ids_json: str) -> dict:
    """Bulk delete multiple clients/members by their IDs.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        client_ids_json: JSON string containing array of client IDs to delete.
            Example: '[1, 2, 3, 4, 5]'

    Returns:
        Summary with success/failure information.
    """
    import json as json_module

    client = get_api_client()
    try:
        client_ids = json_module.loads(client_ids_json)

        if not isinstance(client_ids, list):
            return {"error": "Expected a JSON array of client IDs", "success": False}

        if len(client_ids) == 0:
            return {"error": "No client IDs provided", "success": False}

        # Ensure all IDs are integers
        try:
            client_ids = [int(cid) for cid in client_ids]
        except (ValueError, TypeError):
            return {"error": "All client IDs must be valid numbers", "success": False}

        response = await client.delete("/users/bulk/delete", {"userIds": client_ids})

        return {
            "success": True,
            "message": f"Bulk delete completed: {response.get('deleted', len(client_ids))} clients deleted.",
            "deleted_count": response.get("deleted", len(client_ids)),
            "details": response,
        }
    except json_module.JSONDecodeError:
        return {"error": "Invalid JSON format. Please provide a valid JSON array of IDs.", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
