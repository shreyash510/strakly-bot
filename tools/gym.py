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
