from langchain_core.tools import tool
from .base import get_api_client


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
        response = await client.get("/users", {"role": "manager", "limit": 20})
        return response
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
        # Get managers
        managers = await client.get("/users", {"role": "manager", "limit": 20})
        # Get trainers
        trainers = await client.get("/users", {"role": "trainer", "limit": 20})
        # Get branch admins
        branch_admins = await client.get("/users", {"role": "branch_admin", "limit": 20})

        managers_data = managers.get("data", managers) if isinstance(managers, dict) else managers
        trainers_data = trainers.get("data", trainers) if isinstance(trainers, dict) else trainers
        branch_admins_data = branch_admins.get("data", branch_admins) if isinstance(branch_admins, dict) else branch_admins

        managers_list = managers_data if isinstance(managers_data, list) else []
        trainers_list = trainers_data if isinstance(trainers_data, list) else []
        branch_admins_list = branch_admins_data if isinstance(branch_admins_data, list) else []

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
        # Search in managers
        managers = await client.get("/users", {"role": "manager", "search": search, "limit": 5})
        # Search in trainers
        trainers = await client.get("/users", {"role": "trainer", "search": search, "limit": 5})
        # Search in branch admins
        branch_admins = await client.get("/users", {"role": "branch_admin", "search": search, "limit": 5})

        managers_data = managers.get("data", managers) if isinstance(managers, dict) else managers
        trainers_data = trainers.get("data", trainers) if isinstance(trainers, dict) else trainers
        branch_admins_data = branch_admins.get("data", branch_admins) if isinstance(branch_admins, dict) else branch_admins

        results = []
        if isinstance(managers_data, list):
            for m in managers_data:
                m["staffRole"] = "manager"
                results.append(m)
        if isinstance(trainers_data, list):
            for t in trainers_data:
                t["staffRole"] = "trainer"
                results.append(t)
        if isinstance(branch_admins_data, list):
            for b in branch_admins_data:
                b["staffRole"] = "branch_admin"
                results.append(b)

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
        response = await client.get("/users", {"role": "branch_admin", "limit": 20})
        return response
    except Exception as e:
        return {"error": str(e)}
