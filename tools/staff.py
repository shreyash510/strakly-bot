import asyncio
from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id, generate_password, extract_list


@tool
async def get_managers_list() -> dict:
    """Get list of managers.

    Use this tool when user asks about:
    - List of managers
    - How many managers do I have?
    - Manager information
    - Who are my managers
    - Show managers
    """
    client = get_api_client()
    try:
        response = await client.get("/users", {"role": "manager", "noPagination": "true"})
        managers = extract_list(response)

        if len(managers) == 0:
            return {"count": 0, "managers": [], "message": "No managers found."}

        return {
            "count": len(managers),
            "managers": [{"id": m.get("id"), "name": m.get("name"), "email": m.get("email"), "status": m.get("status")} for m in managers],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_staff_list() -> dict:
    """Get list of all staff members (managers, trainers, branch admins).

    Use this tool when user asks about:
    - List of staff
    - All staff members
    - How many staff do I have?
    - Team members
    - Employees
    """
    client = get_api_client()
    try:
        # Fetch all roles in parallel
        managers, trainers, branch_admins = await asyncio.gather(
            client.get("/users", {"role": "manager", "noPagination": "true"}),
            client.get("/users", {"role": "trainer", "noPagination": "true"}),
            client.get("/users", {"role": "branch_admin", "noPagination": "true"}),
        )

        managers_list = extract_list(managers)
        trainers_list = extract_list(trainers)
        branch_admins_list = extract_list(branch_admins)

        return {
            "managers": {
                "count": len(managers_list),
                "data": managers_list
            },
            "trainers": {
                "count": len(trainers_list),
                "data": trainers_list
            },
            "branchAdmins": {
                "count": len(branch_admins_list),
                "data": branch_admins_list
            },
            "totalStaff": len(managers_list) + len(trainers_list) + len(branch_admins_list)
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_staff_details(search: str) -> dict:
    """Get details of a specific staff member (manager, trainer, or branch admin) by name.

    Args:
        search: Staff member name to search for

    Use this tool when user asks about:
    - Details of a specific manager
    - Details of a specific staff member
    - Show me staff member X information
    """
    client = get_api_client()
    try:
        # Search all roles in parallel
        managers, trainers, branch_admins = await asyncio.gather(
            client.get("/users", {"role": "manager", "search": search, "noPagination": "true"}),
            client.get("/users", {"role": "trainer", "search": search, "noPagination": "true"}),
            client.get("/users", {"role": "branch_admin", "search": search, "noPagination": "true"}),
        )

        results = []
        for role, data in [("manager", managers), ("trainer", trainers), ("branch_admin", branch_admins)]:
            for item in extract_list(data):
                item["staffRole"] = role
                results.append(item)

        return {
            "count": len(results),
            "data": results
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_branch_admins_list() -> dict:
    """Get list of branch admins.

    Use this tool when user asks about:
    - List of branch admins
    - How many branch admins do I have?
    - Branch admin information
    - Who are my branch admins
    """
    client = get_api_client()
    try:
        response = await client.get("/users", {"role": "branch_admin", "noPagination": "true"})
        admins = extract_list(response)

        if len(admins) == 0:
            return {"count": 0, "branchAdmins": [], "message": "No branch admins found."}

        return {
            "count": len(admins),
            "branchAdmins": [{"id": a.get("id"), "name": a.get("name"), "email": a.get("email"), "status": a.get("status")} for a in admins],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_staff(
    name: str,
    email: str,
    role: str,
    phone: str = None,
    gender: str = None,
) -> dict:
    """Create a new staff member (manager, trainer, or branch admin).

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Full name of the staff member (required)
        email: Email address (required)
        role: Staff role - must be one of: manager, trainer, branch_admin (required)
        phone: Phone number (optional)
        gender: Gender - male, female, or other (optional)

    Returns:
        Success response with created staff details, or error message
    """
    # Validate role
    valid_roles = ["manager", "trainer", "branch_admin"]
    if role not in valid_roles:
        return {
            "error": f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}",
            "success": False
        }

    client = get_api_client()
    try:
        # Generate a temporary password
        temp_password = generate_password()

        # Prepare the data
        data = {
            "name": name,
            "email": email,
            "password": temp_password,
            "role": role,
            "status": "active",
        }

        # Add optional fields if provided
        if phone:
            data["phone"] = phone
        if gender and gender in ["male", "female", "other"]:
            data["gender"] = gender

        # Add branch ID if available from context
        branch_id = get_current_branch_id()
        if branch_id:
            data["branchIds"] = [branch_id]

        # Create the user via POST /users
        response = await client.post("/users", data)

        # Get role display name
        role_names = {
            "manager": "Manager",
            "trainer": "Trainer",
            "branch_admin": "Branch Admin"
        }
        role_display = role_names.get(role, role)

        return {
            "success": True,
            "message": f"{role_display} created successfully",
            "staff": {
                "id": response.get("id"),
                "name": response.get("name"),
                "email": response.get("email"),
                "phone": response.get("phone"),
                "role": role,
                "roleDisplay": role_display,
                "status": "active",
            },
            "temp_password": temp_password,
        }
    except Exception as e:
        return {"error": str(e), "success": False}
