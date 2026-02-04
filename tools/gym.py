from langchain_core.tools import tool
from .base import get_api_client, get_current_branch_id


@tool
async def get_gym_info() -> dict:
    """Get information about the current gym.

    Use this tool when user asks about:
    - Gym information
    - Gym details
    - My gym profile
    """
    client = get_api_client()
    try:
        response = await client.get("/gyms/profile")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_branches_info() -> dict:
    """Get information about gym branches.

    Use this tool when user asks about:
    - Branches
    - How many branches do I have?
    - Branch list
    - Branch details
    """
    client = get_api_client()
    try:
        # First get gym profile to get gym_id
        profile = await client.get("/gyms/profile")
        gym_id = profile.get("id", 1) if isinstance(profile, dict) else 1
        response = await client.get(f"/gyms/{gym_id}/branches")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_current_branch() -> dict:
    """Get information about the currently selected branch.

    Use this tool when user asks about:
    - Current branch
    - Which branch am I on?
    - What branch is selected?
    - Selected branch
    - Active branch

    Returns the branch that is currently selected in the app.
    All data queries are filtered by this branch.
    """
    client = get_api_client()
    branch_id = get_current_branch_id()

    if branch_id is None:
        return {"message": "No branch is currently selected. Data is showing for all branches."}

    try:
        # Get branch details
        profile = await client.get("/gyms/profile")
        gym_id = profile.get("id", 1) if isinstance(profile, dict) else 1
        response = await client.get(f"/gyms/{gym_id}/branches")

        branches = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(branches, list):
            for branch in branches:
                if branch.get("id") == branch_id:
                    return {
                        "currentBranch": branch,
                        "branchId": branch_id,
                        "message": f"Currently viewing data for branch: {branch.get('name')}"
                    }

        return {"branchId": branch_id, "message": f"Branch ID {branch_id} is selected but details not found."}
    except Exception as e:
        return {"branchId": branch_id, "error": str(e)}
