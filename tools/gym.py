from langchain_core.tools import tool
from .base import get_api_client


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
